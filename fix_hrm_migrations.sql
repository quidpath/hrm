-- SQL script to manually fix HRM payroll migration issues
-- Run this script if you need to manually fix the database state

-- First, check what columns exist in payroll_payrollrun
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'payroll_payrollrun' 
AND column_name IN ('drafted_at', 'posted_at', 'posted_by')
ORDER BY column_name;

-- Add missing columns safely (only if they don't exist)
ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS drafted_at TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_at TIMESTAMP WITH TIME ZONE NULL;
ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_by UUID NULL;

-- Create indexes safely
CREATE INDEX IF NOT EXISTS payroll_payrollrun_state_idx ON payroll_payrollrun (state);

-- Mark the migration as applied to prevent Django from trying to apply it again
INSERT INTO django_migrations (app, name, applied) 
VALUES ('payroll', '0006_ensure_schema_consistency', NOW())
ON CONFLICT (app, name) DO NOTHING;

-- Verify the migration state
SELECT name, applied FROM django_migrations WHERE app = 'payroll' ORDER BY name;