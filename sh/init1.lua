-- Set <leader> to space
vim.g.mapleader = " "
vim.keymap.set("n", "<leader>n", ":Neotree toggle<CR>", { silent = true, noremap = true })

-- Basic settings
vim.cmd [[syntax enable]]
vim.cmd [[nnoremap q :q<CR>]]
vim.opt.background = "dark"
vim.cmd [[colorscheme sorbet]]
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.scrolloff = 3
vim.opt.cursorline = true
vim.opt.incsearch = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.clipboard = "unnamedplus"
vim.opt.encoding = "utf-8"
vim.opt.fileencoding = "utf-8"
vim.opt.title = true
vim.opt.laststatus = 2

-- Set terminal title to parent/filename
vim.api.nvim_create_autocmd("BufEnter", {
  command = "silent! lcd %:p:h | let &titlestring = fnamemodify(expand('%:p'), ':h:t') . '/' . expand('%:t')"
})

-- Set a minimal statusline
vim.api.nvim_create_autocmd("VimEnter", {
  callback = function()
    vim.opt.statusline = "%t %m (%{fnamemodify(expand('%:p:h'),':t')}/%{expand('%:t')}) %{substitute(system('git rev-parse --abbrev-ref HEAD 2>/dev/null'), '\\n', '', 'g')} spaces=%{&shiftwidth} %=%l,%c (%p%%)"
  end
})

-- Plugin manager bootstrap (lazy.nvim)
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    lazypath
  })
end
vim.opt.rtp:prepend(lazypath)

-- Just Neo-tree
require("lazy").setup({
  {
    "nvim-neo-tree/neo-tree.nvim",
    branch = "v3.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-tree/nvim-web-devicons",
      "MunifTanjim/nui.nvim"
    },
    config = function()
      require("neo-tree").setup({
        window = {
          width = 30, -- << This sets the Neo-tree sidebar width
        }
      })
      vim.keymap.set("n", "<leader>n", ":Neotree toggle<CR>", { silent = true })
    end
  }
})


vim.api.nvim_create_autocmd("FileType", {
  pattern = "*",
  callback = function()
    vim.opt_local.tabstop = 2
    vim.opt_local.shiftwidth = 2
    vim.opt_local.softtabstop = 2
    vim.opt_local.expandtab = true
  end,
})
