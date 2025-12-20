"""
Django management command to fix session_token column length
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix session_token column to support longer JWT tokens'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check current column type
            cursor.execute("""
                SELECT data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'user_sessions'
                AND column_name = 'session_token'
            """)
            
            result = cursor.fetchone()
            if result:
                data_type, max_length = result
                self.stdout.write(f"Current type: {data_type}, max_length: {max_length}")
                
                if data_type == 'character varying' and max_length == 255:
                    # Change to TEXT
                    self.stdout.write("Changing session_token from VARCHAR(255) to TEXT...")
                    cursor.execute("""
                        ALTER TABLE user_sessions 
                        ALTER COLUMN session_token TYPE TEXT
                    """)
                    self.stdout.write(self.style.SUCCESS('Successfully changed session_token to TEXT'))
                elif data_type == 'text':
                    self.stdout.write(self.style.SUCCESS('session_token is already TEXT'))
                else:
                    self.stdout.write(self.style.WARNING(f'session_token has unexpected type: {data_type}'))
            else:
                self.stdout.write(self.style.ERROR('session_token column not found'))

