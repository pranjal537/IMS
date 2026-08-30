"""
Intern Management System - Damak Municipality
Project Configuration Package
"""
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
