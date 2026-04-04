import subprocess, sys, os

# Find node and npm from homebrew
NODE_BIN = '/opt/homebrew/bin'
env = os.environ.copy()
env['PATH'] = NODE_BIN + ':' + env.get('PATH', '')

cmd = sys.argv[1:]
result = subprocess.run(
    ['/opt/homebrew/bin/npm'] + cmd,
    cwd='/Users/carlossanchez/Downloads/presupuestador-backend/.claude/worktrees/serene-wozniak/frontend',
    env=env,
    timeout=300
)
sys.exit(result.returncode)
