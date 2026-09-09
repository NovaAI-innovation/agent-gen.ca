import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ConnectWalletButton } from "@/components/wallet/ConnectWalletButton";

// Mock stores and wallet hooks
vi.mock("@solana/wallet-adapter-react", () => ({
  useWallet: vi.fn(() => ({
    wallets: [],
    select: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
    publicKey: null,
    connected: false,
    connecting: false,
    disconnecting: false,
    signMessage: null,
  })),
  ConnectionProvider: ({ children }: { children: React.ReactNode }) => children,
  WalletProvider: ({ children }: { children: React.ReactNode }) => children,
}));

vi.mock("@/store/authStore", () => ({
  useAuthStore: vi.fn(() => ({
    token: null,
    user: null,
    setToken: vi.fn(),
    fetchMe: vi.fn(),
    logout: vi.fn(),
  })),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

describe("ConnectWalletButton", () => {
  it("shows Connect Wallet button when not signed in", () => {
    render(<ConnectWalletButton />);
    expect(screen.getByText("Connect Wallet")).toBeDefined();
  });
});