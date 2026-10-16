-- Shared options live in ~/.vimrc, which nvim reads as vimscript.
-- Only nvim-specific things belong below.
vim.cmd.source("~/.vimrc")

-- netrw ---------------------------------------------------------------
vim.g.netrw_banner = 0
vim.g.netrw_liststyle = 3
vim.g.netrw_browse_split = 4
vim.g.netrw_winsize = 15

-- keymaps -------------------------------------------------------------
vim.keymap.set("n", "Q", ":quitall<CR>", { noremap = true, silent = true })
vim.keymap.set("n", "<leader>s", ":set spell!<CR>", { silent = true })

-- shada -------------------------------------------------------------
-- EDITOR runs us with --clean, which sets shadafile=NONE.  Put marks,
-- registers and : / history back; --clean is for the rtp, not for that.
vim.opt.shadafile = ""
