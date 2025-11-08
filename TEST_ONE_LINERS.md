# One-Liner Installer Tests

## Fixed: Interactive Prompts Now Work! ✓

All `read` commands now use `</dev/tty` to properly handle piped input from `curl | bash`.

---

## Test Locally First (Before Pushing)

### 1. Test Interactive Mode (Will Ask Questions)
```bash
cd /tmp && bash /Users/pcstyle/agentsdk/install.sh
```

**Expected prompts:**
- Install directory? [/Users/pcstyle/.local/lifeline]
- OpenAI API key? (or press Enter to skip)
- Create 'lifeline' command alias? [Y/n]
- Alias name? [lifeline]
- Add .venv/bin to PATH? [y/N]
- Create desktop shortcut? [y/N]

### 2. Test Mode (No Prompts, Auto-cleanup)
```bash
bash /Users/pcstyle/agentsdk/install.sh --test
```

**Expected:**
- Creates temp dir
- Runs auto-tests
- Cleans up automatically
- No user interaction needed

### 3. Help
```bash
bash /Users/pcstyle/agentsdk/install.sh --help
```

### 4. Uninstall
```bash
bash /Users/pcstyle/agentsdk/install.sh --uninstall
```

**Expected prompts:**
- Enter LifeLine installation directory: (or press Enter to search)
- Delete /path/to/installation? [y/N]

---

## After Pushing to GitHub

Once you've pushed your changes, test these remote one-liners:

### 1. Interactive Install (Default)
```bash
curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash
```

**Should now prompt you interactively!** ✓

### 2. Test Mode
```bash
curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash -s -- --test
```

### 3. Help
```bash
curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash -s -- --help
```

### 4. Uninstall
```bash
curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash -s -- --uninstall
```

### 5. Custom Repo URL
```bash
LIFELINE_REPO_URL=https://github.com/custom/repo.git \
curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash
```

### 6. Custom Branch
```bash
LIFELINE_BRANCH=develop \
curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash
```

---

## What Changed?

### Before (Broken):
```bash
read -r result
# ↑ Fails silently when piped from curl, uses default
```

### After (Fixed):
```bash
read -r result </dev/tty
# ↑ Reads directly from terminal, works with curl | bash
```

### Files Fixed:
- `install.sh` - Line 143: uninstall prompt
- `scripts/install_lifeline.sh` - Lines 149, 157, 175, 278: all interactive prompts

---

## Quick Verification

Test that prompts actually wait for input:

```bash
# This should pause and wait for you to type
cd /tmp && bash /Users/pcstyle/agentsdk/install.sh

# You should see interactive prompts like:
# Install directory [/Users/pcstyle/.local/lifeline]: _
# (cursor waits for input)
```

Press Ctrl+C to cancel if you don't want to complete the install.

---

## Now Try It!

1. **Test locally first** to verify prompts work:
   ```bash
   cd /tmp && bash /Users/pcstyle/agentsdk/install.sh
   ```

2. **If prompts work**, you're good to push and test remotely

3. **After pushing**, test the curl one-liner:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/pc-style/lifeline/main/install.sh | bash
   ```

You should see all the interactive prompts! ✓
