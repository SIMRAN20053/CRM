import React from 'react';
import { Bell, User } from 'lucide-react';

export default function Header() {
  return (
    <header className="flex h-16 shrink-0 items-center gap-x-4 border-b border-border bg-card px-6 shadow-sm">
      <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6 justify-end items-center">
        <button type="button" className="-m-2.5 p-2.5 text-muted-foreground hover:text-foreground transition-colors">
          <span className="sr-only">View notifications</span>
          <Bell className="h-5 w-5" aria-hidden="true" />
        </button>
        <div className="h-6 w-px bg-border" aria-hidden="true" />
        <div className="flex items-center gap-x-4">
          <button type="button" className="flex items-center p-1.5 hover:bg-muted rounded-full transition-colors">
            <span className="sr-only">Open user menu</span>
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
              <User className="h-5 w-5 text-primary" />
            </div>
          </button>
        </div>
      </div>
    </header>
  );
}
