import { pgTable, bigserial, varchar, bigint, text, uuid, integer, date, foreignKey } from 'drizzle-orm/pg-core';

export const userIDTable = pgTable('netaid-users', {
  id: bigserial('id', { mode: 'number' }).primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  password: varchar('password', { length: 100 }).notNull(),
  aadhar_no: bigint('aadhar_no', { mode: 'number' }).notNull(),
});

// export const agenciesTable = pgTable('netaid-agencies', {
//   name: varchar('name', { length: 100 }).notNull(),
//   category: text('category').notNull(),
//   address: varchar('address', { length: 200 }).notNull(),
//   phone_number: bigint('phone_number', { mode: 'number' }).notNull(),
//   email: varchar('email', { length: 100 }).notNull(),
//   area: text('area').notNull(),
//   agency_id: bigint('agency_ID', { mode: 'number' }).notNull(),
//   aid: uuid('aid').notNull(),
//   meta: integer('meta').notNull(),
// });
//
// export const metaTable = pgTable('netaid-meta', {
//   aid: foreignKey("aid", agenciesTable),
//   location: text('location').notNull(),
//   resources_available: text('resources_available').notNull(),
//   last_activity: date('last_activity').notNull(),
// });
//
// export const userInfoTable = pgTable('netaid-user_info', {
//   user_id: foreignKey('user_id', userIDTable),
//   state: text('state').notNull(),
//   city: text('city').notNull(),
//   district: text('district').notNull(),
//   postal_address: bigint('postal_address', { mode: 'number' }).notNull(),
//   address: varchar('address', { length: 200 }).notNull(),
// });
//
