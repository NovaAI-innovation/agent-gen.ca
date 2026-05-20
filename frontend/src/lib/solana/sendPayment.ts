import { Connection, PublicKey, SystemProgram, Transaction } from "@solana/web3.js";
import type { WalletContextState } from "@solana/wallet-adapter-react";

/**
 * Build and send a SOL transfer transaction.
 *
 * @returns The transaction signature string once the transaction is confirmed.
 * @throws If the wallet is not connected, user rejects the transaction, or
 *         the transaction fails on-chain.
 */
export async function sendSolPayment(
  connection: Connection,
  wallet: WalletContextState,
  recipientAddress: string,
  lamports: number,
): Promise<string> {
  if (!wallet.publicKey || !wallet.sendTransaction) {
    throw new Error("Wallet not connected");
  }

  const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash();

  const transaction = new Transaction({
    recentBlockhash: blockhash,
    feePayer: wallet.publicKey,
  }).add(
    SystemProgram.transfer({
      fromPubkey: wallet.publicKey,
      toPubkey: new PublicKey(recipientAddress),
      lamports,
    })
  );

  const signature = await wallet.sendTransaction(transaction, connection);

  const confirmation = await connection.confirmTransaction(
    { signature, blockhash, lastValidBlockHeight },
    "confirmed"
  );

  if (confirmation.value.err) {
    throw new Error(`Transaction failed on-chain: ${JSON.stringify(confirmation.value.err)}`);
  }

  return signature;
}
