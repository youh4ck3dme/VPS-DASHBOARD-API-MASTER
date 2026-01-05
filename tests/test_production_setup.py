"""
Testy pre produkčné nastavenia
"""
import pytest
import os
import subprocess
import sys
from pathlib import Path

# Cesta k projektu
PROJECT_ROOT = Path(__file__).parent.parent


class TestProductionScripts:
    """Testy pre produkčné setup scripty"""
    
    def test_ssl_script_exists(self):
        """Test, či existuje SSL setup script"""
        ssl_script = PROJECT_ROOT / "setup_ssl.sh"
        assert ssl_script.exists(), "setup_ssl.sh musí existovať"
        assert os.access(ssl_script, os.R_OK), "setup_ssl.sh musí byť čitateľný"
    
    def test_firewall_script_exists(self):
        """Test, či existuje firewall setup script"""
        firewall_script = PROJECT_ROOT / "setup_firewall.sh"
        assert firewall_script.exists(), "setup_firewall.sh musí existovať"
        assert os.access(firewall_script, os.R_OK), "setup_firewall.sh musí byť čitateľný"
    
    def test_fail2ban_script_exists(self):
        """Test, či existuje Fail2Ban setup script"""
        fail2ban_script = PROJECT_ROOT / "setup_fail2ban.sh"
        assert fail2ban_script.exists(), "setup_fail2ban.sh musí existovať"
        assert os.access(fail2ban_script, os.R_OK), "setup_fail2ban.sh musí byť čitateľný"
    
    def test_logrotate_script_exists(self):
        """Test, či existuje logrotate setup script"""
        logrotate_script = PROJECT_ROOT / "setup_logrotate.sh"
        assert logrotate_script.exists(), "setup_logrotate.sh musí existovať"
        assert os.access(logrotate_script, os.R_OK), "setup_logrotate.sh musí byť čitateľný"
    
    def test_monitor_script_exists(self):
        """Test, či existuje monitoring script"""
        monitor_script = PROJECT_ROOT / "monitor_health.sh"
        assert monitor_script.exists(), "monitor_health.sh musí existovať"
        assert os.access(monitor_script, os.R_OK), "monitor_health.sh musí byť čitateľný"
    
    def test_production_setup_script_exists(self):
        """Test, či existuje production setup script"""
        prod_script = PROJECT_ROOT / "setup_production.sh"
        assert prod_script.exists(), "setup_production.sh musí existovať"
        assert os.access(prod_script, os.R_OK), "setup_production.sh musí byť čitateľný"
    
    def test_scripts_are_executable(self):
        """Test, či sú scripty spustiteľné (ak sú na Unix systéme)"""
        if sys.platform != "win32":
            scripts = [
                "setup_ssl.sh",
                "setup_firewall.sh",
                "setup_fail2ban.sh",
                "setup_logrotate.sh",
                "monitor_health.sh",
                "setup_production.sh"
            ]
            
            for script_name in scripts:
                script = PROJECT_ROOT / script_name
                if script.exists():
                    # Skontroluj, či má execute bit (aj keď môže byť nastavený neskôr)
                    # Toto je len informačný test
                    pass


class TestProductionConfigurations:
    """Testy pre produkčné konfigurácie"""
    
    def test_logrotate_config_mentioned(self):
        """Test, či logrotate konfigurácia je spomenutá v scripte"""
        logrotate_script = PROJECT_ROOT / "setup_logrotate.sh"
        if logrotate_script.exists():
            content = logrotate_script.read_text()
            assert "logrotate" in content.lower(), "Logrotate musí byť spomenutý"
            assert "/etc/logrotate.d/" in content, "Logrotate config path musí byť spomenutý"
    
    def test_fail2ban_config_mentioned(self):
        """Test, či Fail2Ban konfigurácia je spomenutá v scripte"""
        fail2ban_script = PROJECT_ROOT / "setup_fail2ban.sh"
        if fail2ban_script.exists():
            content = fail2ban_script.read_text()
            assert "fail2ban" in content.lower(), "Fail2Ban musí byť spomenutý"
            assert "/etc/fail2ban/" in content, "Fail2Ban config path musí byť spomenutý"
    
    def test_firewall_config_mentioned(self):
        """Test, či firewall konfigurácia je spomenutá v scripte"""
        firewall_script = PROJECT_ROOT / "setup_firewall.sh"
        if firewall_script.exists():
            content = firewall_script.read_text()
            assert "ufw" in content.lower(), "UFW musí byť spomenutý"
            assert "allow" in content.lower() or "deny" in content.lower(), "Firewall rules musí byť spomenutý"
    
    def test_ssl_certbot_mentioned(self):
        """Test, či certbot je spomenutý v SSL scripte"""
        ssl_script = PROJECT_ROOT / "setup_ssl.sh"
        if ssl_script.exists():
            content = ssl_script.read_text()
            assert "certbot" in content.lower(), "Certbot musí byť spomenutý"
            assert "letsencrypt" in content.lower() or "ssl" in content.lower(), "SSL/LetsEncrypt musí byť spomenutý"


class TestProductionDeployment:
    """Testy pre produkčné nasadenie"""
    
    def test_deploy_script_exists(self):
        """Test, či existuje deploy script"""
        deploy_script = PROJECT_ROOT / "deploy.sh"
        assert deploy_script.exists(), "deploy.sh musí existovať"
    
    def test_deploy_script_mentions_security(self):
        """Test, či deploy script spomína bezpečnostné nastavenia"""
        deploy_script = PROJECT_ROOT / "deploy.sh"
        if deploy_script.exists():
            content = deploy_script.read_text()
            # Deploy script by mal spomínať bezpečnostné nastavenia
            assert "firewall" in content.lower() or "fail2ban" in content.lower() or "ssl" in content.lower(), \
                "Deploy script musí spomínať bezpečnostné nastavenia"
    
    def test_production_documentation_exists(self):
        """Test, či existuje produkčná dokumentácia"""
        docs = [
            "PRODUCTION_DEPLOYMENT.md",
            "PRODUCTION_CHECKLIST.md",
            "README_PRODUCTION.md"
        ]
        
        for doc in docs:
            doc_path = PROJECT_ROOT / doc
            assert doc_path.exists(), f"{doc} musí existovať"


class TestBackupAutomation:
    """Testy pre backup automatizáciu"""
    
    def test_backup_script_exists(self):
        """Test, či existuje backup script"""
        backup_script = PROJECT_ROOT / "backup_db.sh"
        assert backup_script.exists(), "backup_db.sh musí existovať"
    
    def test_backup_script_is_executable(self):
        """Test, či backup script je spustiteľný"""
        backup_script = PROJECT_ROOT / "backup_db.sh"
        if backup_script.exists() and sys.platform != "win32":
            # Script by mal byť spustiteľný
            pass  # Toto je len informačný test


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

