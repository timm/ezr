-- netrw -------------------------------------------------------------
vim.g.netrw_banner = 0
vim.g.netrw_liststyle = 3
vim.g.netrw_browse_split = 4
vim.g.netrw_winsize = 15

-- ui / editing ------------------------------------------------------
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.cursorline = true
vim.opt.mouse = "a"
vim.opt.clipboard = "unnamedplus"

vim.opt.ignorecase = true
vim.opt.smartcase = true

vim.opt.expandtab = true
vim.opt.tabstop = 2
vim.opt.shiftwidth = 2

vim.opt.splitright = true
vim.opt.splitbelow = true


vim.g.netrw_banner = 0

-- undo --------------------------------------------------------------
vim.opt.undofile = true
vim.opt.undodir = vim.fn.expand("~/.vim/undo")

-- statusline --------------------------------------------------------
vim.opt.statusline =
  "%#StatusLine# ▶ %f %m%r%=%y ❖ %l:%c ❖ %p%% "

vim.opt.laststatus = 2

-- keymaps -----------------------------------------------------------
vim.keymap.set("n", "Q", ":quitall<CR>", { noremap = true, silent = true })

-- Toggle spelling with <Leader>s (usually \s)
vim.keymap.set("n", "<leader>s", ":set spell!<CR>", { silent = true })

-- colors ------------------------------------------------------------
vim.cmd.colorscheme("sorbet")

