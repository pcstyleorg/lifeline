# Next.js 16 + Tailwind CSS v4 Template

> 🚀 A modern, Vercel-ready template with Next.js 16 and Tailwind CSS v4

This is a GitHub template repository. You can use it in multiple ways:

- **Use as GitHub Template**: Click the "Use this template" button to create a new repository
- **Use with create-next-app**: Use this template directly with Next.js CLI (see below)

## Features

- ⚡ Next.js 16 with App Router
- 🎨 Tailwind CSS v4
- 📦 TypeScript
- 🚀 Vercel-ready deployment
- 🔧 pnpm package manager
- ✅ ESLint configured
- 🤖 GitHub Actions CI workflow

## Quick Start

### Option 1: Using create-next-app (Recommended)

Use this template directly with the Next.js CLI:

```bash
npx create-next-app@latest --example "https://github.com/pc-style/template" my-app
cd my-app
./run
```

This will create a new Next.js project using this template. The `create-next-app` CLI will handle the setup automatically.

**Note**: Make sure to replace `my-app` with your desired project name.

### Option 2: Using GitHub Template

1. Click the **"Use this template"** button on GitHub
2. Create a new repository from this template
3. Clone your new repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```
4. Run the setup script:
   ```bash
   ./run
   ```

### Option 3: Manual Clone

```bash
# Clone the repository
git clone https://github.com/pc-style/template.git my-app
cd my-app

# Run the setup script (auto-installs pnpm and dependencies)
./run

# Or manually:
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) to see your app.

> **Learn more**: See the [Next.js documentation](https://nextjs.org/docs/app/api-reference/cli/create-next-app#with-any-public-github-example) on using GitHub examples with `create-next-app`.

## Available Scripts

Use the `./run` script for convenience, or use pnpm directly:

```bash
./run          # Start development server (default)
./run install  # Install dependencies
./run build    # Build for production
./run start    # Start production server
./run lint     # Run linter
```

Or with pnpm directly:

```bash
pnpm dev       # Start development server
pnpm build     # Build for production
pnpm start     # Start production server
pnpm lint      # Run linter
```

## Deploy on Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/your-repo)

Or use the Vercel CLI:

```bash
vercel
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

