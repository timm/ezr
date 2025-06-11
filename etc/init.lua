-- Essential Neovim settings for a clean and efficient workflow
vim.opt.termguicolors = true
vim.opt.tabstop = 2
vim.opt.shiftwidth = 2
vim.opt.expandtab = true
vim.opt.softtabstop = 2
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.mouse = "a"
vim.opt.undofile = true
vim.opt.undodir = os.getenv("HOME") .. "/.nvim/undodir"
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.incsearch = true
vim.opt.hlsearch = true
vim.opt.cursorline = true
vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.errorbells = false
vim.opt.visualbell = true
vim.opt.wildmenu = true
vim.opt.wildmode = "list:longest,full"
vim.opt.smartindent = true
vim.opt.title = true
vim.opt.clipboard = "unnamedplus"

vim.opt.wrap = true
vim.opt.linebreak = true   -- wrap at word boundaries
vim.opt.breakindent = true -- preserve indent on wrapped lines

vim.o.sidescrolloff = 999
vim.o.sidescroll = 1

vim.api.nvim_create_autocmd("TermOpen", {
  pattern = "*",
  command = "startinsert"
})

vim.g.mapleader = " "
vim.g.maplocalleader = " "

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  { "catppuccin/nvim", name = "catppuccin", priority = 1000 },
  { "MunifTanjim/nui.nvim" },
  {
    "nvim-tree/nvim-tree.lua",
    version = "*",
    lazy = false,
    config = function()
      require("nvim-tree").setup {}
    end,
  },
  {
    "nvim-telescope/telescope.nvim",
    branch = "master",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      require("telescope").setup {}
    end,
  },
  {
    "lewis6991/gitsigns.nvim",
    config = function()
      require("gitsigns").setup {}
    end,
  },
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-tree.lua", "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup {
        options = {
          theme = "auto",
        },
        sections = {
          lualine_x = { "filetype", "branch", "diff" },
        },
        tabline = {
          lualine_a = { "buffers" },
          lualine_b = {},
          lualine_c = {},
          lualine_x = {},
          lualine_y = {},
          lualine_z = { "tabs" },
        },
      }
    end,
  },
  {
    "preservim/nerdcommenter",
    lazy = false,
  },
  {
    "folke/noice.nvim",
    event = "VeryLazy",
    opts = {},
    dependencies = {
      "MunifTanjim/nui.nvim",
      "rcarriga/nvim-notify",
      "nvim-tree/nvim-web-devicons",
    },
  },
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      require("nvim-treesitter.configs").setup({
        ensure_installed = { "c", "cpp", "lua", "vim", "vimdoc", "query", "javascript", "typescript", "html", "css", "json", "yaml", "markdown" },
        sync_install = false,
        auto_install = true,
        highlight = {
          enable = true,
          additional_vim_regex_highlighting = false,
        },
        indent = {
          enable = true,
        },
      })
    end,
  },
  {
    "stevearc/conform.nvim",
    lazy = false,
    opts = {},
  },
  -- LSP setup (Python + Lua)
  {
    "neovim/nvim-lspconfig",
    event = { "BufReadPre", "BufNewFile" },
    config = function()
      local lspconfig = require("lspconfig")

      -- Pyright: consistent, quiet Python LSP
      lspconfig.pyright.setup({
        settings = {
          python = {
            analysis = {
              typeCheckingMode = "off",
              diagnosticMode = "openFilesOnly",
              autoSearchPaths = true,
              useLibraryCodeForTypes = true,
            },
          },
        },
      })

      -- Lua LSP: quiet diagnostics for Neovim development
      lspconfig.lua_ls.setup({
        settings = {
          Lua = {
            diagnostics = {
              globals = { "vim" },
            },
          },
        },
      })
    end
  },
  {
    "hrsh7th/nvim-cmp",
    event = "InsertEnter",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "L3MON4D3/LuaSnip"
    },
    config = function()
      local cmp = require("cmp")
      cmp.setup {
        mapping = cmp.mapping.preset.insert({
          ["<Tab>"] = cmp.mapping.confirm({ select = true }),
        }),
        sources = {
          { name = "nvim_lsp" },
        },
      }
    end
  }
})

require("catppuccin").setup({
  flavour = "mocha",
})
vim.cmd.colorscheme "catppuccin"

vim.keymap.set("n", "<C-n>", ":NvimTreeToggle<CR>", { desc = "Toggle NvimTree" })
vim.keymap.set("n", "<leader>ff", "<cmd>Telescope find_files<cr>", { desc = "Find files" })
vim.keymap.set("n", "<leader>fg", "<cmd>Telescope live_grep<cr>", { desc = "Live Grep" })
vim.keymap.set("n", "<leader>c", ":NERDCommenterComment<CR>", { desc = "Comment/Uncomment line(s)" })
vim.keymap.set("n", "<C-h>", "<C-w>h", { desc = "Move to left window" })
vim.keymap.set("n", "<C-j>", "<C-w>j", { desc = "Move to lower window" })
vim.keymap.set("n", "<C-k>", "<C-w>k", { desc = "Move to upper window" })
vim.keymap.set("n", "<C-l>", "<C-w>l", { desc = "Move to right window" })

vim.api.nvim_create_autocmd("TextYankPost", {
  callback = function()
    vim.highlight.on_yank({
      higroup = "IncSearch",
      timeout = 200,
    })
  end,
  group = vim.api.nvim_create_augroup("YankHighlight", { clear = true }),
})

vim.keymap.set("n", "[b", ":bprevious<CR>", { desc = "Previous buffer" })
vim.keymap.set("n", "]b", ":bnext<CR>", { desc = "Next buffer" })
vim.keymap.set("n", "<leader>nh", ":nohlsearch<CR>", { desc = "Clear search highlights" })
vim.keymap.set("n", "<leader>tn", ":set relativenumber!<CR>:set number!<CR>", { desc = "Toggle relative/absolute line numbers" })

vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  callback = function()
    vim.bo.tabstop = 2
    vim.bo.shiftwidth = 2
    vim.bo.expandtab = true
    vim.bo.softtabstop = 2
  end,
})

vim.api.nvim_create_autocmd("TermOpen", {
  pattern = "*",
  group = vim.api.nvim_create_augroup("UserTermNoModifiable", { clear = true }),
  callback = function()
    vim.opt_local.modifiable = false
  end,
})

vim.diagnostic.config({
  virtual_text = true,
  signs = true,
  underline = true,
  update_in_insert = false,
})

