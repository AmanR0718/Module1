FROM python:3.11-bookworm

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential python3-dev libffi-dev libssl-dev curl \
    && curl https://sh.rustup.rs -sSf | bash -s -- -y \
    && . "$HOME/.cargo/env" \
    && rustup install stable && rustup default stable \
    && export PATH="$HOME/.cargo/bin:$PATH" \
    && RUST_BACKTRACE=1 PATH="$HOME/.cargo/bin:$PATH" \
        python3 -m pip install --no-binary bcrypt --no-cache-dir --force-reinstall bcrypt==4.1.3 \
    && python3 -m pip install passlib[bcrypt]==1.7.4 \
    && apt-get purge -y build-essential python3-dev rustc cargo \
    && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

CMD ["python3", "-c", "\
import sys, bcrypt; \
print('Python:', sys.version); \
print('bcrypt module file:', bcrypt.__file__); \
print('hasattr(bcrypt, __about__):', hasattr(bcrypt, '__about__')); \
print('bcrypt version:', getattr(bcrypt, '__version__', 'n/a')); \
print('bcrypt test hash:', bcrypt.hashpw(b'Admin@123', bcrypt.gensalt()).decode()) \
"]
