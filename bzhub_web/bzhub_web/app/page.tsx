import Image from "next/image";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
          <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center py-32 px-8 bg-white dark:bg-black">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={100}
          height={20}
          priority
        />
        <h1 className="text-4xl font-bold text-center text-black dark:text-zinc-50 mb-4">
          Welcome to BizHub CRM (Web)
        </h1>
        <p className="text-lg text-center text-zinc-700 dark:text-zinc-300 mb-8">
          Your cloud-ready, modular ERP/CRM suite.<br />
          <span className="text-sm text-zinc-500">Frontend: Next.js (Vercel) &nbsp;|&nbsp; Backend: FastAPI (Render) &nbsp;|&nbsp; Database: Supabase</span>
        </p>
        <div className="text-center text-zinc-600 dark:text-zinc-400">
          <p>Get started by editing <code>app/page.tsx</code>.</p>
          <p className="mt-2">See <code>documentation/ARCHITECTURE.md</code> for project design and decisions.</p>
        </div>
      </main>
    </div>
  );
}
