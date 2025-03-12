import typer
import asyncio
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal  
from app.models import Admin
from app.utils.authentication import get_password_hash

app = typer.Typer()
# typer is not async thats we need async and sync function


@app.command()
def create_admin(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    superadmin: bool = typer.Option(False, "--superadmin")
) -> None:
    async def _async_create_admin():
        async with SessionLocal() as db:  
            try:
                # Check for duplicates
                result = await db.execute(select(Admin).where(Admin.email == email))
                if result.scalar_one_or_none():
                    typer.echo(f"Error: Admin {email} already exists!")
                    return

                # Create admin
                admin = Admin(
                    email=email,
                    hashed_password=get_password_hash(password),
                    is_superadmin=superadmin
                )
                db.add(admin)
                await db.commit()
                typer.echo(f"Admin {email} created successfully!")

            except IntegrityError:
                await db.rollback()
                typer.echo("Error: Email already exists!")
            except Exception as e:
                await db.rollback()
                typer.echo(f"Critical error: {str(e)}")

    asyncio.run(_async_create_admin())



if __name__ == "__main__":
    app()