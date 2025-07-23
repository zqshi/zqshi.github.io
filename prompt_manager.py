"""
数字员工系统 - Prompt版本管理工具
版本: 1.0.0
作者: Claude Code
创建时间: 2025-07-23
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PromptVersion:
    """Prompt版本信息"""
    version: str
    date: str
    changes: List[str]
    author: str = "System"


class PromptManager:
    """Prompt版本管理器"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.version_file = self.prompts_dir / "version.json"
        self.ensure_directory()
    
    def ensure_directory(self):
        """确保prompts目录存在"""
        self.prompts_dir.mkdir(exist_ok=True)
    
    def get_version_info(self) -> Dict[str, Any]:
        """获取版本信息"""
        if not self.version_file.exists():
            return self._create_initial_version()
        
        with open(self.version_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_initial_version(self) -> Dict[str, Any]:
        """创建初始版本信息"""
        initial_version = {
            "version": "1.0.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "description": "数字员工系统Prompt版本管理",
            "changes": [],
            "prompts": {}
        }
        self.save_version_info(initial_version)
        return initial_version
    
    def save_version_info(self, version_info: Dict[str, Any]):
        """保存版本信息"""
        with open(self.version_file, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)
    
    def load_prompt_file(self, filename: str) -> Dict[str, Any]:
        """加载prompt文件"""
        file_path = self.prompts_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_prompt_file(self, filename: str, data: Dict[str, Any]):
        """保存prompt文件"""
        file_path = self.prompts_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_agent_prompt(self, agent_type: str) -> Dict[str, Any]:
        """获取指定Agent的prompt配置"""
        try:
            agent_prompts = self.load_prompt_file("agent_prompts.json")
            if agent_type in agent_prompts.get("agents", {}):
                return agent_prompts["agents"][agent_type]
            else:
                raise ValueError(f"Agent type not found: {agent_type}")
        except FileNotFoundError:
            raise ValueError(f"Agent prompts file not found")
    
    def get_system_prompt(self, prompt_name: str) -> Dict[str, Any]:
        """获取系统prompt"""
        try:
            system_prompts = self.load_prompt_file("system_prompts.json")
            if prompt_name in system_prompts.get("prompts", {}):
                return system_prompts["prompts"][prompt_name]
            else:
                raise ValueError(f"System prompt not found: {prompt_name}")
        except FileNotFoundError:
            raise ValueError(f"System prompts file not found")
    
    def get_constraint_prompt(self, constraint_type: str, constraint_name: str) -> Dict[str, Any]:
        """获取约束prompt"""
        try:
            constraint_prompts = self.load_prompt_file("constraint_prompts.json")
            constraints = constraint_prompts.get("constraints", {})
            if constraint_type in constraints and constraint_name in constraints[constraint_type]:
                return constraints[constraint_type][constraint_name]
            else:
                raise ValueError(f"Constraint prompt not found: {constraint_type}.{constraint_name}")
        except FileNotFoundError:
            raise ValueError(f"Constraint prompts file not found")
    
    def get_task_prompt(self, task_category: str, task_type: str) -> Dict[str, Any]:
        """获取任务prompt"""
        try:
            task_prompts = self.load_prompt_file("task_prompts.json")
            tasks = task_prompts.get("task_templates", {})
            if task_category in tasks and task_type in tasks[task_category]:
                return tasks[task_category][task_type]
            else:
                raise ValueError(f"Task prompt not found: {task_category}.{task_type}")
        except FileNotFoundError:
            raise ValueError(f"Task prompts file not found")
    
    def render_prompt(self, template: str, variables: Dict[str, str] = None) -> str:
        """渲染prompt模板"""
        if variables is None:
            variables = {}
        
        try:
            return template.format(**variables)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    def update_version(self, new_version: str, changes: List[str], author: str = "System"):
        """更新版本信息"""
        version_info = self.get_version_info()
        
        # 添加新版本记录
        if "changes" not in version_info:
            version_info["changes"] = []
        
        version_info["changes"].append({
            "version": new_version,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "changes": changes,
            "author": author
        })
        
        # 更新当前版本
        version_info["version"] = new_version
        version_info["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        self.save_version_info(version_info)
    
    def create_agent_prompt(self, agent_id: str, role: str) -> str:
        """为指定Agent创建完整的prompt"""
        try:
            # 获取Agent配置
            agent_config = self.get_agent_prompt(role)
            
            # 获取系统基础prompt
            base_system = self.get_system_prompt("base_agent_system")
            
            # 获取约束条件
            constraints = []
            
            # 根据Agent类型获取相应约束
            if role in ["hr_agent"]:
                constraints.append(self.get_constraint_prompt("business_constraints", "hr_ethics"))
                constraints.append(self.get_constraint_prompt("security_constraints", "privacy_protection"))
            elif role in ["finance_agent"]:
                constraints.append(self.get_constraint_prompt("business_constraints", "financial_approval"))
            elif role in ["legal_agent"]:
                constraints.append(self.get_constraint_prompt("business_constraints", "legal_compliance"))
            elif role in ["developer_agent", "architect_agent"]:
                constraints.append(self.get_constraint_prompt("technical_constraints", "code_quality"))
            elif role in ["devops_agent"]:
                constraints.append(self.get_constraint_prompt("technical_constraints", "production_safety"))
            
            # 所有Agent都需要数据访问控制约束
            constraints.append(self.get_constraint_prompt("security_constraints", "data_access_control"))
            constraints.append(self.get_constraint_prompt("escalation_rules", "human_intervention"))
            
            # 构建约束文本
            constraint_text = "\n\n".join([constraint["template"] for constraint in constraints])
            
            # 渲染最终prompt
            final_prompt = self.render_prompt(
                base_system["template"],
                {
                    "role": agent_config["role_name"],
                    "role_description": agent_config["system_prompt"],
                    "capabilities": "\n".join([f"- {cap}" for cap in agent_config["capabilities"]]),
                    "constraints": constraint_text
                }
            )
            
            return final_prompt
            
        except Exception as e:
            raise ValueError(f"Failed to create agent prompt: {str(e)}")
    
    def create_task_prompt(self, agent_role: str, task_type: str, task_data: Dict[str, Any]) -> str:
        """为任务创建专用prompt"""
        try:
            # 根据Agent角色确定任务类别
            task_category_mapping = {
                "hr_agent": "hr_tasks",
                "finance_agent": "finance_tasks",
                "developer_agent": "technical_tasks",
                "devops_agent": "technical_tasks",
                "architect_agent": "technical_tasks"
            }
            
            task_category = task_category_mapping.get(agent_role, "general_tasks")
            
            # 获取任务prompt模板
            if task_category != "general_tasks":
                try:
                    task_prompt = self.get_task_prompt(task_category, task_type)
                except ValueError:
                    # 如果找不到专用模板，使用通用模板
                    task_prompt = self.get_task_prompt("general_tasks", "task_planning")
            else:
                task_prompt = self.get_task_prompt("general_tasks", "task_planning")
            
            # 渲染任务prompt
            return self.render_prompt(task_prompt["template"], task_data)
            
        except Exception as e:
            raise ValueError(f"Failed to create task prompt: {str(e)}")
    
    def validate_prompts(self) -> Dict[str, List[str]]:
        """验证所有prompt文件的完整性"""
        validation_results = {
            "errors": [],
            "warnings": [],
            "info": []
        }
        
        try:
            # 检查版本文件
            version_info = self.get_version_info()
            validation_results["info"].append(f"Current version: {version_info.get('version', 'Unknown')}")
            
            # 检查各个prompt文件
            required_files = [
                "system_prompts.json",
                "agent_prompts.json", 
                "constraint_prompts.json",
                "task_prompts.json"
            ]
            
            for filename in required_files:
                try:
                    data = self.load_prompt_file(filename)
                    validation_results["info"].append(f"[OK] {filename} loaded successfully")
                    
                    # 检查版本信息
                    if "version" not in data:
                        validation_results["warnings"].append(f"Missing version info in {filename}")
                    
                except FileNotFoundError:
                    validation_results["errors"].append(f"Missing required file: {filename}")
                except json.JSONDecodeError:
                    validation_results["errors"].append(f"Invalid JSON format in {filename}")
            
            # 测试Agent prompt创建
            test_agents = ["hr_agent", "finance_agent", "developer_agent"]
            for agent in test_agents:
                try:
                    prompt = self.create_agent_prompt(f"test_{agent}", agent)
                    validation_results["info"].append(f"[OK] {agent} prompt creation successful")
                except Exception as e:
                    validation_results["errors"].append(f"Failed to create {agent} prompt: {str(e)}")
            
        except Exception as e:
            validation_results["errors"].append(f"Validation failed: {str(e)}")
        
        return validation_results
    
    def list_available_prompts(self) -> Dict[str, List[str]]:
        """列出所有可用的prompt"""
        available_prompts = {
            "system_prompts": [],
            "agent_types": [],
            "constraint_types": [],
            "task_types": []
        }
        
        try:
            # 系统prompts
            system_prompts = self.load_prompt_file("system_prompts.json")
            available_prompts["system_prompts"] = list(system_prompts.get("prompts", {}).keys())
            
            # Agent类型
            agent_prompts = self.load_prompt_file("agent_prompts.json")
            available_prompts["agent_types"] = list(agent_prompts.get("agents", {}).keys())
            
            # 约束类型
            constraint_prompts = self.load_prompt_file("constraint_prompts.json")
            constraints = constraint_prompts.get("constraints", {})
            for category, items in constraints.items():
                for item in items.keys():
                    available_prompts["constraint_types"].append(f"{category}.{item}")
            
            # 任务类型
            task_prompts = self.load_prompt_file("task_prompts.json")
            tasks = task_prompts.get("task_templates", {})
            for category, items in tasks.items():
                for item in items.keys():
                    available_prompts["task_types"].append(f"{category}.{item}")
            
        except Exception as e:
            print(f"Error listing prompts: {str(e)}")
        
        return available_prompts


# 使用示例和测试函数
if __name__ == "__main__":
    # 创建prompt管理器实例
    pm = PromptManager()
    
    print("=== 数字员工系统 Prompt 管理工具 ===\n")
    
    # 验证prompt系统
    print("1. 验证Prompt系统...")
    validation = pm.validate_prompts()
    
    for error in validation["errors"]:
        print(f"[ERROR] {error}")
    
    for warning in validation["warnings"]:
        print(f"[WARNING] {warning}")
    
    for info in validation["info"]:
        print(f"[INFO] {info}")
    
    print("\n" + "="*50 + "\n")
    
    # 列出可用prompts
    print("2. 可用Prompt类型:")
    available = pm.list_available_prompts()
    
    for category, items in available.items():
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"  - {item}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试创建Agent prompt
    print("3. 测试创建Agent Prompt:")
    try:
        hr_prompt = pm.create_agent_prompt("hr_001", "hr_agent")
        print("[SUCCESS] HR Agent prompt创建成功")
        print(f"Prompt长度: {len(hr_prompt)} 字符\n")
        
        # 显示prompt预览（前500字符）
        print("Prompt预览:")
        print("-" * 40)
        print(hr_prompt[:500] + "..." if len(hr_prompt) > 500 else hr_prompt)
        print("-" * 40)
        
    except Exception as e:
        print(f"[ERROR] HR Agent prompt创建失败: {str(e)}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试任务prompt
    print("4. 测试任务Prompt创建:")
    try:
        task_data = {
            "employee_id": "EMP001",
            "analysis_type": "performance_review"
        }
        task_prompt = pm.create_task_prompt("hr_agent", "employee_analysis", task_data)
        print("[SUCCESS] 任务prompt创建成功")
        print(f"Prompt长度: {len(task_prompt)} 字符")
        
    except Exception as e:
        print(f"[ERROR] 任务prompt创建失败: {str(e)}")
    
    print("\n版本管理工具测试完成！")