# EZR in Julia - All functionality in clean, idiomatic Julia
using Random, Statistics, StatsBase, CSV, DataFrames
using Printf: @sprintf

# Configuration as a simple struct
@kwdef mutable struct Config
    seed::Int = 1234567891
    any::Int = 4
    budget::Int = 30
    check::Int = 5
    few::Int = 128
    leaf::Int = 3
    bins::Int = 7
    m::Int = 2
    p::Int = 2
    ks::Float64 = 0.95
    delta::String = "smed"
    acq::String = "xploit" end

const the = Config()

# Column type that handles both numeric and symbolic data
mutable struct Col
    pos::Int
    name::String
    is_numeric::Bool
    is_goal::Bool
    is_class::Bool
    is_skip::Bool
    n::Int
    values::Vector
    # Numeric stats
    lo::Union{Float64, Nothing}
    hi::Union{Float64, Nothing}
    mu::Float64
    m2::Float64
    # Symbolic stats
    counts::Union{Dict{Any,Int}, Nothing}
    
    function Col(pos::Int, name::String)
        is_numeric = isuppercase(name[1])
        is_goal = endswith(name, '-') || endswith(name, '+') || endswith(name, '!')
        is_class = endswith(name, '!')
        is_skip = endswith(name, 'X')
        
        if is_numeric
            new(pos, name, is_numeric, is_goal, is_class, is_skip, 0, [],
                Inf, -Inf, 0.0, 0.0, nothing)
        else
            new(pos, name, is_numeric, is_goal, is_class, is_skip, 0, [],
                nothing, nothing, 0.0, 0.0, Dict{Any,Int}()) end end end

function add!(col::Col, val)
    val == "?" && return
    push!(col.values, val)
    col.n += 1
    if col.is_numeric
        col.lo = min(col.lo, val)
        col.hi = max(col.hi, val)
        # Online mean/variance update
        delta = val - col.mu
        col.mu += delta / col.n
        col.m2 += delta * (val - col.mu)
    else
        col.counts[val] = get(col.counts, val, 0) + 1 end end

mid(col::Col) = col.is_numeric ? col.mu : 
    isempty(col.counts) ? nothing : findmax(col.counts)[2]

function div(col::Col)
    if col.is_numeric
        col.n > 1 ? sqrt(col.m2 / (col.n - 1)) : 0.0
    else
        isempty(col.counts) && return 0.0
        total = sum(values(col.counts))
        -sum(p * log2(p) for p in [c/total for c in values(col.counts)] if p > 0)
    end
end

norm(col::Col, val) = (val == "?" || !col.is_numeric) ? val : 
    (val - col.lo) / (col.hi - col.lo + 1e-32)

function likelihood(col::Col, val)
    val == "?" && return log(1e-32)
    
    if col.is_numeric
        col.n == 0 && return log(1e-32)
        sd = div(col)
        sd == 0 && return log(1e-32)
        
        # Gaussian likelihood
        var = sd^2 + 1e-32
        -0.5 * ((val - col.mu)^2 / var + log(2π * var))
    else
        # Categorical likelihood with m-estimate
        count = get(col.counts, val, 0)
        total = sum(values(col.counts))
        prior = isempty(col.counts) ? 1.0 : 1.0 / length(col.counts)
        prob = (count + the.m * prior) / (total + the.m)
        log(max(prob, 1e-32))
    end
end

# Main Data structure
mutable struct Data
    rows::Vector{Vector}
    cols::Vector{Col}
    n::Int
    cache::Dict{String, Any}
    
    Data() = new(Vector{Vector}[], Col[], 0, Dict{String, Any}())
end

function Data(source::String)
    data = Data()
    df = CSV.read(source, DataFrame)
    init_from_header!(data, names(df))
    for row in eachrow(df)
        add!(data, collect(row))
    end
    data
end

function Data(rows::Vector{Vector{T}}) where T
    data = Data()
    if length(rows) > 0 && eltype(rows[1]) == String
        # First row is header
        init_from_header!(data, rows[1])
        for row in rows[2:end]
            add!(data, row)
        end
    else
        # All data rows - assume generic header
        for row in rows
            add!(data, row)
        end
    end
    data
end

function init_from_header!(data::Data, header)
    data.cols = [Col(i, string(name)) for (i, name) in enumerate(header)]
end

function add!(data::Data, row)
    push!(data.rows, row)
    data.n += 1
    empty!(data.cache)  # invalidate cache
    
    for col in data.cols
        col.pos <= length(row) && add!(col, row[col.pos])
    end
    data
end

function clone(data::Data, rows=nothing)
    new_data = Data()
    new_data.cols = [Col(col.pos, col.name) for col in data.cols]
    
    if rows !== nothing
        for row in rows
            add!(new_data, row)
        end
    end
    new_data
end

# Convenience accessors
x_cols(data::Data) = [col for col in data.cols if !col.is_skip && !col.is_goal]
y_cols(data::Data) = [col for col in data.cols if col.is_goal]
klass_col(data::Data) = findfirst(col -> col.is_class, data.cols)

# Distance functions
function heaven_distance(data::Data, row)
    goals = y_cols(data)
    isempty(goals) && return 0.0
    
    d = 0.0
    for col in goals
        if col.pos <= length(row)
            val = norm(col, row[col.pos])
            if val != "?" && isa(val, Real)
                # Minimize if ends with '-', maximize if ends with '+'
                target = endswith(col.name, '-') ? 0.0 : 1.0
                d += abs(val - target)^the.p
            end
        end
    end
    (d / length(goals))^(1/the.p)
end

function row_distance(data::Data, row1, row2)
    xcols = x_cols(data)
    isempty(xcols) && return 0.0
    
    d = 0.0
    for col in xcols
        if col.pos <= length(row1) && col.pos <= length(row2)
            a, b = row1[col.pos], row2[col.pos]
            if a == "?" && b == "?"
                d += 1
            elseif col.is_numeric
                a = a != "?" ? norm(col, a) : (norm(col, b) > 0.5 ? 0 : 1)
                b = b != "?" ? norm(col, b) : (norm(col, a) > 0.5 ? 0 : 1)
                d += abs(a - b)^the.p
            else
                d += (a != b)
            end
        end
    end
    (d / length(xcols))^(1/the.p)
end

function row_likelihood(data::Data, row)
    prior = log(data.n / (100 + 1e-32))  # dataset size prior
    feature_likelihood = sum(likelihood(col, row[col.pos]) 
                           for col in x_cols(data) if col.pos <= length(row))
    prior + feature_likelihood
end

# Core EZR Algorithm
function likely(data::Data; acq="xploit", budget=30)
    # Initialize with random sample
    shuffle!(data.rows)
    labeled_rows = data.rows[1:the.any]
    unlabeled = data.rows[the.any+1:end]
    
    # Split labeled into best and rest
    sort!(labeled_rows, by=row -> heaven_distance(data, row))
    cut = Int(floor(sqrt(the.any)))
    best = clone(data, labeled_rows[1:cut])
    rest = clone(data, labeled_rows[cut+1:end])
    
    # Active learning loop
    while best.n < budget && !isempty(unlabeled)
        # Score unlabeled examples
        candidates = length(unlabeled) > the.few*2 ? 
                    sample(unlabeled, the.few*2, replace=false) : unlabeled
        
        scores = Float64[]
        for row in candidates
            b_like = row_likelihood(best, row)
            r_like = row_likelihood(rest, row)
            
            score = if acq == "klass"
                b_like - r_like
            elseif acq == "near"
                b_dist = minimum(row_distance(best, row, r) for r in best.rows)
                r_dist = minimum(row_distance(rest, row, r) for r in rest.rows)
                r_dist - b_dist
            elseif acq == "bore"
                b, r = exp(b_like), exp(r_like)
                b^2 / (r + 1e-32)
            else  # xploit, xplor, adapt
                b, r = exp(b_like), exp(r_like)
                p = best.n / budget
                q = acq == "xploit" ? 0.0 : acq == "xplor" ? 1.0 : 1-p
                (b + r*q) / abs(b*q - r + 1e-32)
            end
            push!(scores, score)
        end
        
        # Select best candidate
        best_idx = argmax(scores)
        pick = candidates[best_idx]
        
        # Remove from unlabeled and add to best
        filter!(x -> x != pick, unlabeled)
        add!(best, pick)
        
        # Rebalance if best group too big
        if best.n > sqrt(best.n + rest.n)
            sort!(best.rows, by=row -> heaven_distance(best, row))
            worst = pop!(best.rows)
            best.n -= 1
            add!(rest, worst)
        end
    end
    
    length(best.rows) >= the.check ? best.rows[1:the.check] : best.rows
end

# Tree structures
mutable struct TreeNode
    data::Union{Data, Nothing}
    ys_mu::Float64
    kids::Vector{TreeNode}
    how::Union{Tuple{String, Col, Any}, Nothing}
    
    TreeNode(data=nothing, ys_mu=0.0) = new(data, ys_mu, TreeNode[], nothing)
end

function build_tree(data::Data; Y=nothing, leaf=nothing)
    leaf = leaf === nothing ? the.leaf : leaf
    Y = Y === nothing ? row -> heaven_distance(data, row) : Y
    
    tree = TreeNode(data, mean(Y(r) for r in data.rows))
    
    if data.n >= leaf
        best_split = find_best_split(data, Y)
        if best_split !== nothing
            op, col, val, conditions = best_split
            for condition in conditions
                subset_rows = [r for r in data.rows if satisfies(r, condition)]
                if leaf <= length(subset_rows) < data.n
                    subset = clone(data, subset_rows)
                    child = build_tree(subset, Y=Y, leaf=leaf)
                    child.how = condition
                    push!(tree.kids, child)
                end
            end
        end
    end
    
    tree
end

function find_best_split(data::Data, Y)
    best_score = Inf
    best_split = nothing
    
    for col in x_cols(data)
        if col.is_numeric
            # Numeric splits
            values = sort(unique([row[col.pos] for row in data.rows 
                                if col.pos <= length(row) && row[col.pos] != "?"]))
            for i in 2:length(values)
                val = values[i-1]
                left = [r for r in data.rows if col.pos <= length(r) && 
                       r[col.pos] != "?" && r[col.pos] <= val]
                right = [r for r in data.rows if col.pos <= length(r) && 
                        r[col.pos] != "?" && r[col.pos] > val]
                
                if the.leaf <= length(left) <= data.n - the.leaf
                    score = split_score(left, right, Y)
                    if score < best_score
                        best_score = score
                        best_split = ("<=", col, val, [("<=", col, val), (">", col, val)])
                    end
                end
            end
        else
            # Categorical splits
            values = unique([row[col.pos] for row in data.rows 
                           if col.pos <= length(row) && row[col.pos] != "?"])
            conditions = [("==", col, val) for val in values]
            subsets = [[r for r in data.rows if satisfies(r, cond)] for cond in conditions]
            
            if all(length(s) >= the.leaf for s in subsets)
                score = sum(length(s) * var([Y(r) for r in s]) for s in subsets) / data.n
                if score < best_score
                    best_score = score
                    best_split = (nothing, col, nothing, conditions)
                end
            end
        end
    end
    
    best_split
end

function satisfies(row, condition)
    op, col, val = condition
    col.pos > length(row) || row[col.pos] == "?" && return false
    
    row_val = row[col.pos]
    op == "<=" ? row_val <= val :
    op == ">" ? row_val > val :
    op == "==" ? row_val == val : false
end

function split_score(left, right, Y)
    isempty(left) || isempty(right) && return Inf
    
    left_var = var([Y(r) for r in left])
    right_var = var([Y(r) for r in right])
    (length(left) * left_var + length(right) * right_var) / (length(left) + length(right))
end

function show_tree(tree::TreeNode; depth=0, baseline=nothing)
    if depth == 0
        println(@sprintf("%6s %4s", "#rows", "win"))
        baseline = tree.ys_mu
    end
    
    for child in tree.kids
        op, col, val = child.how
        indent = "| " ^ depth
        is_leaf = isempty(child.kids)
        
        score = Int(100 * (1 - (child.ys_mu - baseline) / (baseline + 1e-32)))
        leaf_marker = is_leaf ? ";" : ""
        
        n_rows = child.data === nothing ? 0 : child.data.n
        println(@sprintf("%6d %4d    %sif %s %s %s%s", 
                        n_rows, score, indent, col.name, op, val, leaf_marker))
        
        if !is_leaf
            show_tree(child, depth=depth+1, baseline=baseline)
        end
    end
end

# Classification
function classify(data::Data, test_data; method="bayes")
    klass_idx = klass_col(data)
    klass_idx === nothing && error("No class column found")
    
    # Build class models
    classes = Dict{Any, Data}()
    for row in data.rows
        klass = row[klass_idx.pos]
        if !haskey(classes, klass)
            classes[klass] = clone(data)
        end
        add!(classes[klass], row)
    end
    
    # Classify test instances
    test_rows = isa(test_data, Data) ? test_data.rows : test_data
    [findmax(k -> row_likelihood(classes[k], test_row) for k in keys(classes))[2] 
     for test_row in test_rows]
end

# Statistical tests
mutable struct ConfusionMatrix
    classes::Dict{Any, NamedTuple}
    total::Int
    
    ConfusionMatrix() = new(Dict(), 0)
end

function confuse!(cf::ConfusionMatrix, want, got)
    for x in (want, got)
        if !haskey(cf.classes, x)
            cf.classes[x] = (label=x, tn=cf.total, fn=0, fp=0, tp=0)
        end
    end
    
    for (label, stats) in cf.classes
        if label == want
            tp = stats.tp + (got == want ? 1 : 0)
            fn = stats.fn + (got != want ? 1 : 0)
            cf.classes[label] = (label=label, tn=stats.tn, fn=fn, fp=stats.fp, tp=tp)
        else
            fp = stats.fp + (got == label ? 1 : 0)
            tn = stats.tn + (got != label ? 1 : 0)
            cf.classes[label] = (label=label, tn=tn, fn=stats.fn, fp=fp, tp=stats.tp)
        end
    end
    cf.total += 1
end

function confusion_metrics(cf::ConfusionMatrix)
    results = Dict{Any, NamedTuple}()
    
    for (label, stats) in cf.classes
        precision = stats.tp + stats.fp > 0 ? 100 * stats.tp / (stats.tp + stats.fp) : 0.0
        recall = stats.tp + stats.fn > 0 ? 100 * stats.tp / (stats.tp + stats.fn) : 0.0
        f1 = precision + recall > 0 ? 2 * precision * recall / (precision + recall) : 0.0
        accuracy = cf.total > 0 ? 100 * (stats.tp + stats.tn) / cf.total : 0.0
        
        results[label] = (
            label=label, precision=precision, recall=recall, f1=f1, accuracy=accuracy,
            tp=stats.tp, fp=stats.fp, tn=stats.tn, fn=stats.fn
        )
    end
    
    results
end

function statistical_same(x::Vector, y::Vector; ks_alpha=0.05, cliffs_threshold="medium")
    x, y = sort(x), sort(y)
    n, m = length(x), length(y)
    
    # Cliff's Delta
    function cliffs_delta()
        gt = sum(a > b for a in x, b in y)
        lt = sum(a < b for a in x, b in y)
        abs(gt - lt) / (n * m)
    end
    
    # Kolmogorov-Smirnov test
    function ks_test()
        all_vals = sort(unique([x; y]))
        fx = [sum(a <= v for a in x) / n for v in all_vals]
        fy = [sum(a <= v for a in y) / m for v in all_vals]
        maximum(abs(v1 - v2) for (v1, v2) in zip(fx, fy))
    end
    
    # Thresholds
    ks_critical = Dict(0.1 => 1.22, 0.05 => 1.36, 0.01 => 1.63)[ks_alpha]
    cliffs_thresh = Dict("small" => 0.11, "medium" => 0.28, "large" => 0.43)[cliffs_threshold]
    
    cliffs = cliffs_delta()
    ks_stat = ks_test()
    ks_critical_val = ks_critical * sqrt((n + m) / (n * m))
    
    (cliffs_delta=cliffs, ks_statistic=ks_stat, 
     same=(cliffs <= cliffs_thresh && ks_stat <= ks_critical_val))
end

# Experiment runners
function optimize_experiment(data::Data; acqs=["xploit", "xplor", "adapt", "klass", "near"], 
                           budgets=[10, 20, 30, 40, 80], repeats=20)
    baseline = mean(heaven_distance(data, r) for r in data.rows)
    results = Dict{Tuple{String, Int}, NamedTuple}()
    
    for acq in acqs, budget in budgets
        scores = Float64[]
        for rep in 1:repeats
            Random.seed!(the.seed + rep)  # reproducible
            best_rows = likely(data, acq=acq, budget=budget)
            if !isempty(best_rows)
                best_score = minimum(heaven_distance(data, r) for r in best_rows)
                win = Int(100 * (1 - best_score / baseline))
                push!(scores, win)
            end
        end
        
        results[(acq, budget)] = (
            mean=mean(scores), 
            std=std(scores), 
            scores=scores
        )
    end
    
    results
end

# Text processing (simplified)
mutable struct TextProcessor
    docs::Vector{NamedTuple}
    vocab::Dict{String, Int}
    df::Dict{String, Int}  # document frequency
    
    TextProcessor() = new(NamedTuple[], Dict{String,Int}(), Dict{String,Int}())
end

function add_doc!(tp::TextProcessor, text::String, label::String)
    tokens = simple_tokenize(text)
    doc = (text=text, label=label, tokens=tokens)
    push!(tp.docs, doc)
    
    # Update vocabulary
    for token in unique(tokens)
        tp.df[token] = get(tp.df, token, 0) + 1
    end
    for token in tokens
        tp.vocab[token] = get(tp.vocab, token, 0) + 1
    end
end

function simple_tokenize(text::String)
    words = String[]
    for word in split(lowercase(text))
        word = filter(isalpha, word)
        if length(word) > 2
            push!(words, word)
        end
    end
    words
end

function to_data(tp::TextProcessor; top_k=50)
    # Calculate TF-IDF scores
    n_docs = length(tp.docs)
    tfidf = Dict{String, Float64}()
    
    for (word, df) in tp.df
        idf = log(n_docs / df)
        tfidf[word] = sum(count(==(word), doc.tokens) * idf for doc in tp.docs)
    end
    
    # Get top features
    top_words = [word for (word, score) in sort(collect(tfidf), by=x->x[2], rev=true)[1:min(top_k, length(tfidf))]]
    
    # Create data
    header = ["label!"; [uppercasefirst(w) for w in top_words]]
    rows = Vector{Vector}([string.(header)])
    
    for doc in tp.docs
        row = Any[doc.label]
        for word in top_words
            push!(row, count(==(word), doc.tokens))
        end
        push!(rows, row)
    end
    
    Data(rows)
end

# Simple example
function run_example()
    println("EZR Julia Example")
    println("=================")
    
    # Create sample data
    data = Data([
        ["Weight", "Height", "Age", "Health-"],  # Header
        [70.0, 170.0, 25.0, 80.0],
        [80.0, 180.0, 30.0, 75.0], 
        [60.0, 160.0, 35.0, 85.0],
        [90.0, 190.0, 40.0, 70.0]
    ])
    
    println("Loaded $(data.n) rows with $(length(data.cols)) columns")
    println("\nBest rows from optimization:")
    
    best = likely(data, acq="xploit", budget=3)
    for row in best
        dist = heaven_distance(data, row)
        println("  $row -> heaven_dist=$(round(dist, digits=3))")
    end
    
    println("\nDecision tree:")
    tree = build_tree(data)
    show_tree(tree)
    
    println("\nExperiment results:")
    results = optimize_experiment(data, budgets=[2,3,4], repeats=5)
    for ((acq, budget), result) in results
        println("$acq/$budget: $(round(result.mean, digits=1))±$(round(result.std, digits=1))")
    end
end

# Run example if called directly
if abspath(PROGRAM_FILE) == @__FILE__
    run_example()
end
