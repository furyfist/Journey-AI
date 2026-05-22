export default function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <div className="max-w-screen-xl mx-auto px-4 sm:px-6 w-full">
      {children}
    </div>
  );
}
