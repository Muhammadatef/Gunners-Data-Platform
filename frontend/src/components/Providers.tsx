'use client';

import Header from './Header';
import Footer from './Footer';

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      {children}
      <Footer />
    </>
  );
}
