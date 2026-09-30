"""Generate local secrets without overwriting a pre-existing configuration."""
from pathlib import Path
import secrets


def main():
    root = Path(__file__).resolve().parents[1]
    target = root / '.env'
    if target.exists():
        print('.env ya existe; no se modificó. Si JWT_SECRET está vacío, completa la clave.')
        return
    template = (root / '.env.example').read_text(encoding='utf-8')
    target.write_text(template.replace('JWT_SECRET=', 'JWT_SECRET=' + secrets.token_urlsafe(48)),
                      encoding='utf-8')
    print('Configuración local creada. No publiques ni compartas .env.')


if __name__ == '__main__':
    main()
