"""Docker utilities for creating Dockerfile and .dockerignore."""

import os


def create_dockerfile_and_dockerignore(build_dir, project_path, project_type):
    """Create Dockerfile and .dockerignore files."""
    create_dockerfile(build_dir, project_path, project_type)
    create_dockerignore(project_path)


def create_dockerfile(build_dir, project_path, project_type):
    """Create a static Dockerfile for the built application."""
    dockerfile_content = f"""# Static Dockerfile for {project_type} application
FROM nginx:alpine

# Copy built files to nginx html directory
COPY {os.path.basename(build_dir)} /usr/share/nginx/html

# Copy custom nginx configuration if exists
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""
    
    dockerfile_path = os.path.join(project_path, 'Dockerfile')
    
    try:
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        print(f"Created Dockerfile at {dockerfile_path}")
        return dockerfile_path
    except Exception as e:
        print(f"Warning: Could not create Dockerfile: {e}")
        return None


def create_dockerignore(project_path):
    """Create a .dockerignore file."""
    dockerignore_content = """node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.nyc_output
.coverage
.vscode
.DS_Store
"""
    
    dockerignore_path = os.path.join(project_path, '.dockerignore')
    
    try:
        with open(dockerignore_path, 'w') as f:
            f.write(dockerignore_content)
        print(f"Created .dockerignore at {dockerignore_path}")
        return dockerignore_path
    except Exception as e:
        print(f"Warning: Could not create .dockerignore: {e}")
        return None
 
