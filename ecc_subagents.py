import os
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

ECC_SUBAGENTS = {
    "architect": {
        "name": "Architect & Planner Agent",
        "description": "System architecture design, component structuring, and plan creation",
        "role": "Chief Software Architect",
        "prompt": "Anda adalah Chief Software Architect. Tugas Anda adalah meriset struktur codebase, membuat implementation_plan.md, merancang arsitektur komponen, dan memastikan desain software bersih, modular, serta memenuhi standar Disk G:\\."
    },
    "tester": {
        "name": "TDD & Test Specialist Agent",
        "description": "Automated unit testing, test-driven development, and quality assurance",
        "role": "QA & Test Automation Lead",
        "prompt": "Anda adalah QA & Test Automation Lead. Tugas Anda adalah membuat suite pengujian otomatis, memverifikasi fungsionalitas dengan PyTest / JS Test Runner, dan memastikan tidak ada regresi atau kegagalan sebelum perilisan."
    },
    "security": {
        "name": "Security & Code Auditor Agent",
        "description": "Vulnerability scanning, token security, and code quality auditing",
        "role": "Cybersecurity & Code Auditor",
        "prompt": "Anda adalah Cybersecurity Auditor. Tugas Anda adalah memeriksa potensi kerentanan keamanan (XSS, Injection, Token exposure), audit memori leak, dan memastikan sanitasi data berjalan aman."
    },
    "bug_hunter": {
        "name": "Bug Hunter & Fixer Agent",
        "description": "Deep traceback analysis, runtime error diagnosis, and root cause fixing",
        "role": "Senior Debugging Specialist",
        "prompt": "Anda adalah Senior Debugging Specialist. Tugas Anda adalah mengekstrak log un-truncated, menganalisis root cause kegagalan runtime, dan memperbaiki bug tanpa menutup-nutupi error atau menggunakan superficial patches."
    },
    "ui_ux": {
        "name": "UI/UX Frontend Specialist Agent",
        "description": "Modern web UI design, glassmorphism CSS, responsive layouts, and animations",
        "role": "Lead Frontend UI/UX Designer",
        "prompt": "Anda adalah Lead Frontend UI/UX Designer. Tugas Anda adalah merancang antarmuka web modern (vibrant colors, Google Fonts, smooth gradients, glassmorphism, responsive CSS) yang memukau pengguna saat pertama kali dilihat."
    }
}

def get_subagent_info(agent_key):
    return ECC_SUBAGENTS.get(agent_key.lower())

def list_all_subagents():
    res = "🤖 *ECC MULTI-SUBAGENT REGISTRY*\n\n"
    for key, data in ECC_SUBAGENTS.items():
        res += f"• *{key.upper()}* ({data['role']})\n  _{data['description']}_\n\n"
    return res

def build_subagent_task_prompt(agent_key, task_desc):
    agent = get_subagent_info(agent_key)
    if not agent:
        return task_desc
    a_name = agent['name'].upper()
    a_role = agent['role']
    a_prompt = agent['prompt']
    return f"[SUBAGENT DELEGATION: {a_name} ({a_role})]\nFOKUS TUGAS: {a_prompt}\n\nDESKRIPSI TUGAS DARI USER:\n{task_desc}\n"

if __name__ == "__main__":
    print(list_all_subagents())
