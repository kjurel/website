import { drizzle } from 'drizzle-orm/postgres-js'
import * as schema from './schema/netaid'
import postgres from 'postgres'

console.log()
const connectionString = import.meta.env.DATABASE_URI!

// Disable prefetch as it is not supported for "Transaction" pool mode
const client = postgres(connectionString, { prepare: false })
export const db = drizzle(client , {schema});
