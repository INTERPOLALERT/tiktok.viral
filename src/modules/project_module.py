"""
Project Management Module
Manage content projects, templates, and workflows
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import shutil

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manage content creation projects"""

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.projects_dir = Path(__file__).parent.parent.parent / "data" / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Project manager initialized")

    async def create_project(
        self,
        name: str,
        description: str,
        project_type: str = "video",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new project"""
        logger.info(f"Creating project: {name}")

        project_data = {
            "name": name,
            "description": description,
            "type": project_type,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "assets": {
                "videos": [],
                "images": [],
                "audio": [],
                "scripts": []
            }
        }

        # Create project directory
        project_slug = name.lower().replace(" ", "_")
        project_dir = self.projects_dir / project_slug
        project_dir.mkdir(exist_ok=True)

        # Create asset subdirectories
        for asset_type in ["videos", "images", "audio", "scripts"]:
            (project_dir / asset_type).mkdir(exist_ok=True)

        # Save project metadata
        project_file = project_dir / "project.json"
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)

        # Save to database
        if self.db_session:
            from ..database.models import Project
            db_project = Project(
                name=name,
                description=description,
                type=project_type,
                status="active",
                metadata=project_data
            )
            self.db_session.add(db_project)
            self.db_session.commit()
            project_data["id"] = db_project.id

        logger.info(f"Project created: {project_slug}")
        return project_data

    async def get_project(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get project details"""
        logger.info(f"Getting project: {project_name}")

        project_slug = project_name.lower().replace(" ", "_")
        project_file = self.projects_dir / project_slug / "project.json"

        if project_file.exists():
            with open(project_file, 'r') as f:
                return json.load(f)

        return None

    async def list_projects(
        self,
        status: Optional[str] = None,
        project_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all projects"""
        logger.info("Listing projects")

        projects = []

        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                project_file = project_dir / "project.json"
                if project_file.exists():
                    with open(project_file, 'r') as f:
                        project_data = json.load(f)

                    # Apply filters
                    if status and project_data.get("status") != status:
                        continue
                    if project_type and project_data.get("type") != project_type:
                        continue

                    projects.append(project_data)

        # Sort by updated_at
        projects.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        logger.info(f"Found {len(projects)} projects")
        return projects

    async def update_project(
        self,
        project_name: str,
        **updates
    ) -> Optional[Dict[str, Any]]:
        """Update project details"""
        logger.info(f"Updating project: {project_name}")

        project = await self.get_project(project_name)
        if not project:
            return None

        # Update fields
        for key, value in updates.items():
            if key in project:
                project[key] = value

        project["updated_at"] = datetime.now().isoformat()

        # Save updated project
        project_slug = project_name.lower().replace(" ", "_")
        project_file = self.projects_dir / project_slug / "project.json"

        with open(project_file, 'w') as f:
            json.dump(project, f, indent=2)

        logger.info(f"Project updated: {project_name}")
        return project

    async def delete_project(self, project_name: str) -> bool:
        """Delete a project"""
        logger.info(f"Deleting project: {project_name}")

        project_slug = project_name.lower().replace(" ", "_")
        project_dir = self.projects_dir / project_slug

        if project_dir.exists():
            shutil.rmtree(project_dir)
            logger.info(f"Project deleted: {project_name}")
            return True

        return False

    async def add_asset_to_project(
        self,
        project_name: str,
        asset_type: str,
        asset_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add an asset to a project"""
        logger.info(f"Adding {asset_type} asset to {project_name}")

        project = await self.get_project(project_name)
        if not project:
            return False

        asset_info = {
            "path": asset_path,
            "name": Path(asset_path).name,
            "added_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        if asset_type not in project["assets"]:
            project["assets"][asset_type] = []

        project["assets"][asset_type].append(asset_info)
        await self.update_project(project_name, assets=project["assets"])

        return True

    async def export_project(
        self,
        project_name: str,
        export_format: str = "zip"
    ) -> str:
        """Export project as archive"""
        logger.info(f"Exporting project: {project_name}")

        project_slug = project_name.lower().replace(" ", "_")
        project_dir = self.projects_dir / project_slug

        if not project_dir.exists():
            raise ValueError(f"Project not found: {project_name}")

        export_dir = self.projects_dir.parent / "exports"
        export_dir.mkdir(exist_ok=True)

        archive_name = f"{project_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        archive_path = export_dir / archive_name

        # Create archive
        shutil.make_archive(str(archive_path), export_format, project_dir)

        logger.info(f"Project exported: {archive_path}.{export_format}")
        return f"{archive_path}.{export_format}"


class TemplateManager:
    """Manage content templates"""

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.templates_dir = Path(__file__).parent.parent.parent / "src" / "assets" / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Template manager initialized")

    async def create_template(
        self,
        name: str,
        template_type: str,
        content: Dict[str, Any],
        thumbnail_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new template"""
        logger.info(f"Creating template: {name}")

        template_data = {
            "name": name,
            "type": template_type,
            "content": content,
            "thumbnail_path": thumbnail_path,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }

        # Save template
        template_slug = name.lower().replace(" ", "_")
        template_file = self.templates_dir / f"{template_slug}.json"

        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2)

        # Save to database
        if self.db_session:
            from ..database.models import Template
            db_template = Template(
                name=name,
                type=template_type,
                content=content,
                thumbnail_path=thumbnail_path
            )
            self.db_session.add(db_template)
            self.db_session.commit()
            template_data["id"] = db_template.id

        logger.info(f"Template created: {name}")
        return template_data

    async def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template by name"""
        template_slug = template_name.lower().replace(" ", "_")
        template_file = self.templates_dir / f"{template_slug}.json"

        if template_file.exists():
            with open(template_file, 'r') as f:
                return json.load(f)

        return None

    async def list_templates(
        self,
        template_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List all templates"""
        logger.info("Listing templates")

        templates = []

        for template_file in self.templates_dir.glob("*.json"):
            with open(template_file, 'r') as f:
                template_data = json.load(f)

            if template_type and template_data.get("type") != template_type:
                continue

            templates.append(template_data)

        templates.sort(key=lambda x: x.get("usage_count", 0), reverse=True)

        return templates

    async def use_template(
        self,
        template_name: str,
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Use a template with optional customizations"""
        logger.info(f"Using template: {template_name}")

        template = await self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Create copy of template content
        content = template["content"].copy()

        # Apply customizations
        if customizations:
            content.update(customizations)

        # Increment usage count
        template["usage_count"] = template.get("usage_count", 0) + 1

        template_slug = template_name.lower().replace(" ", "_")
        template_file = self.templates_dir / f"{template_slug}.json"

        with open(template_file, 'w') as f:
            json.dump(template, f, indent=2)

        return content


class WorkflowManager:
    """Manage content creation workflows"""

    def __init__(self):
        self.workflows = {}
        logger.info("Workflow manager initialized")

    async def create_workflow(
        self,
        name: str,
        steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a workflow"""
        logger.info(f"Creating workflow: {name}")

        workflow = {
            "name": name,
            "steps": steps,
            "created_at": datetime.now().isoformat(),
            "status": "ready"
        }

        self.workflows[name] = workflow
        return workflow

    async def execute_workflow(
        self,
        workflow_name: str,
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow"""
        logger.info(f"Executing workflow: {workflow_name}")

        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_name}")

        workflow = self.workflows[workflow_name]
        workflow["status"] = "running"

        results = {
            "workflow": workflow_name,
            "started_at": datetime.now().isoformat(),
            "steps_completed": [],
            "status": "in_progress"
        }

        # Execute each step
        for i, step in enumerate(workflow["steps"]):
            logger.info(f"Executing step {i+1}: {step.get('name', 'unnamed')}")

            step_result = {
                "step": i + 1,
                "name": step.get("name"),
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }

            results["steps_completed"].append(step_result)

        results["status"] = "completed"
        results["completed_at"] = datetime.now().isoformat()
        workflow["status"] = "ready"

        logger.info(f"Workflow completed: {workflow_name}")
        return results

    def get_predefined_workflows(self) -> List[Dict[str, Any]]:
        """Get predefined workflows"""
        return [
            {
                "name": "Video Creation Workflow",
                "description": "Complete video creation from script to publish",
                "steps": [
                    {"name": "Generate Script", "module": "script"},
                    {"name": "Create Voiceover", "module": "audio"},
                    {"name": "Generate Visuals", "module": "video"},
                    {"name": "Edit and Compile", "module": "video"},
                    {"name": "Optimize for Platform", "module": "social_media"},
                    {"name": "Schedule Post", "module": "social_media"}
                ]
            },
            {
                "name": "Social Media Campaign",
                "description": "Multi-platform content campaign",
                "steps": [
                    {"name": "Trend Research", "module": "trends"},
                    {"name": "Content Strategy", "module": "script"},
                    {"name": "Create Content", "module": "mixed"},
                    {"name": "Optimize for Platforms", "module": "social_media"},
                    {"name": "Schedule Posts", "module": "social_media"},
                    {"name": "Monitor Performance", "module": "analytics"}
                ]
            }
        ]
