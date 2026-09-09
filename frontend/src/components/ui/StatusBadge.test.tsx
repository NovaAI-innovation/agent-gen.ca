import { describe, it, expect } from "vitest";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { render, screen } from "@testing-library/react";

describe("StatusBadge", () => {
  it("renders with default draft status", () => {
    render(<StatusBadge />);
    expect(screen.getByRole("status")).toHaveTextContent(/draft/i);
  });

  it("renders with custom label", () => {
    render(<StatusBadge status="approved" label="Verified" />);
    expect(screen.getByRole("status")).toHaveTextContent(/verified/i);
  });

  it("has accessible aria-label", () => {
    render(<StatusBadge status="pending" />);
    expect(screen.getByRole("status")).toHaveAttribute("aria-label", "pending");
  });
});
