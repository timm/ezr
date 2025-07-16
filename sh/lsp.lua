-- Auto-install nvim-lspconfig if missing
local lazypath = vim.fn.stdpath("data").."/site/pack/lsp/start/nvim-lspconfig"
if vim.fn.empty(vim.fn.glob(lazypath)) > 0 then
  vim.fn.system({
    "git", "clone", "--depth=1",
    "https://github.com/neovim/nvim-lspconfig", lazypath
  })
end
vim.opt.runtimepath:append(lazypath)

-- Setup pyright for Python LSP
require("lspconfig").pyright.setup{}

-- Show diagnostics: inline + underlined + floating on hold
vim.diagnostic.config({
  virtual_text = true,   -- inline message
  signs = true,          -- E/W/etc in sign column
  underline = true,
  update_in_insert = false,
  severity_sort = true,
})

-- Auto float errors after cursor pause
vim.opt.updatetime = 500
vim.api.nvim_create_autocmd("CursorHold", {
  callback = function()
    vim.diagnostic.open_float(nil, { focus = false })
  end
})

-- Key to show diagnostic manually
vim.keymap.set("n", "<leader>e", vim.diagnostic.open_float)

-- === UI + Behavior (from your -c flags) ===
vim.opt.expandtab = true
vim.opt.shiftwidth = 2
vim.opt.tabstop = 2
vim.opt.scrolloff = 3
vim.opt.cursorline = true
vim.opt.hidden = true
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.showmode = false
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.clipboard = "unnamedplus"
vim.opt.background = "dark"
vim.cmd.syntax("enable")
pcall(vim.cmd.colorscheme, "sorbet")  -- fallback-safe

vim.g.netrw_browse_split = 4
vim.g.netrw_liststyle = 3
vim.g.netrw_banner = 0

vim.api.nvim_create_autocmd("VimEnter", {
  command = "Vexplore | vertical resize 25"
})

