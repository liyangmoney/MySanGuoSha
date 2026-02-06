#!/usr/bin/env python3
"""
三国杀服务器启动脚本
"""

import os
import sys
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)