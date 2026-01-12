import ClientProviders from '@/components/ClientProviders';

export const metadata = {
  title: 'Arsenal FC Analytics',
  description: 'Comprehensive football analytics platform for Arsenal FC',
};

export const dynamic = 'force-dynamic';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ClientProviders>{children}</ClientProviders>
      </body>
    </html>
  );
}
