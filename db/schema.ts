import { sqliteTable, text, integer, uniqueIndex } from 'drizzle-orm/sqlite-core';
export const structures=sqliteTable('structures',{id:text('id').primaryKey(),signature:text('signature').notNull(),data:text('data').notNull(),createdAt:integer('created_at').notNull()},t=>[uniqueIndex('idx_structure_signature').on(t.signature)]);
export const bikes=sqliteTable('bikes',{id:text('id').primaryKey(),structureId:text('structure_id').notNull().references(()=>structures.id),data:text('data').notNull(),createdAt:integer('created_at').notNull()});
export const intakes=sqliteTable('intakes',{id:text('id').primaryKey(),data:text('data').notNull(),createdAt:integer('created_at').notNull()});
