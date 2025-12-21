#!/usr/bin/env python3
"""
Windows 11 Release Detection & Monitoring System
Author: kelexine (https://github.com/kelexine)

Monitors multiple sources for new Windows 11 releases and triggers builds.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WindowsRelease:
    """Represents a Windows 11 release"""
    build_id: str
    build_number: str
    version: str
    title: str
    iso_url: str
    detected_date: str
    architecture: str
    channel: str = "retail"
    language: str = "en-us"
    checksum_sha256: Optional[str] = None
    size_bytes: Optional[int] = None


class ReleaseDetector:
    """Detects new Windows 11 releases from multiple sources"""
    
    def __init__(self, tracking_file: str = "tracked_releases.json"):
        self.tracking_file = Path(tracking_file)
        self.tracked_data = self._load_tracked()
        self.sources = [
            self._check_uupdump,
            self._check_microsoft_catalog,
            self._check_github_releases
        ]
    
    def _load_tracked(self) -> Dict:
        """Load previously tracked releases"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in {self.tracking_file}, starting fresh")
        
        return {
            'builds': {},
            'last_check': None,
            'check_count': 0
        }
    
    def _save_tracked(self):
        """Save tracked releases to file"""
        self.tracked_data['last_check'] = datetime.now().isoformat()
        self.tracked_data['check_count'] = self.tracked_data.get('check_count', 0) + 1
        
        with open(self.tracking_file, 'w') as f:
            json.dump(self.tracked_data, f, indent=2)
        
        logger.info(f"✅ Saved tracking data to {self.tracking_file}")
    
    def _check_uupdump(self) -> List[WindowsRelease]:
        """Check UUP Dump API for new releases"""
        logger.info("🔍 Checking UUP Dump...")
        
        try:
            response = requests.get(
                "https://api.uupdump.net/listid.php",
                params={
                    'search': 'Windows 11',
                    'sortByDate': '1'
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            releases = []
            for build in data.get('response', {}).get('builds', [])[:30]:
                build_id = build.get('uuid')
                title = build.get('title', '')
                arch = build.get('arch', '')
                
                # Filter for x64 Windows 11
                if 'Windows 11' not in title or arch != 'amd64':
                    continue
                
                # Skip if already tracked
                if build_id in self.tracked_data.get('builds', {}):
                    continue
                
                # Extract version
                version = self._extract_version(title)
                
                release = WindowsRelease(
                    build_id=build_id,
                    build_number=build.get('build', 'Unknown'),
                    version=version,
                    title=title,
                    iso_url=f"https://uupdump.net/download.php?id={build_id}&pack=en-us&edition=professional",
                    detected_date=datetime.now().isoformat(),
                    architecture=arch,
                    channel='retail' if 'Insider' not in title else 'insider'
                )
                
                releases.append(release)
                logger.info(f"  ✨ Found: {title}")
            
            return releases
            
        except Exception as e:
            logger.error(f"❌ UUP Dump check failed: {e}")
            return []
    
    def _check_microsoft_catalog(self) -> List[WindowsRelease]:
        """Check Microsoft Update Catalog (placeholder)"""
        logger.info("🔍 Checking Microsoft Catalog...")
        
        # This would require web scraping or API access
        # Implementation depends on available endpoints
        # For now, return empty list
        
        return []
    
    def _check_github_releases(self) -> List[WindowsRelease]:
        """Check other GitHub repos for Windows ISOs (placeholder)"""
        logger.info("🔍 Checking GitHub Releases...")
        
        # Check repos like microsoft/Windows-11 or community mirrors
        # Implementation depends on available sources
        
        return []
    
    def _extract_version(self, title: str) -> str:
        """Extract Windows version from title"""
        versions = ['26100', '25398', '24H2', '25H2', '23H2', '22H2']
        
        for ver in versions:
            if ver in title:
                # Normalize to H2 format
                if ver.isdigit():
                    # Build number, try to map
                    if int(ver) >= 26000:
                        return '25H2'
                    elif int(ver) >= 24000:
                        return '24H2'
                return ver
        
        return 'Unknown'
    
    def detect_new_releases(self, force: bool = False) -> List[WindowsRelease]:
        """
        Detect new releases from all sources
        
        Args:
            force: Force check even if recently checked
        
        Returns:
            List of new WindowsRelease objects
        """
        # Check if we should skip (checked recently)
        if not force and self.tracked_data.get('last_check'):
            last_check = datetime.fromisoformat(self.tracked_data['last_check'])
            if datetime.now() - last_check < timedelta(hours=1):
                logger.info("⏭️  Skipping check (checked less than 1 hour ago)")
                return []
        
        all_releases = []
        
        # Check all sources
        for source in self.sources:
            try:
                releases = source()
                all_releases.extend(releases)
            except Exception as e:
                logger.error(f"❌ Source check failed: {e}")
                continue
        
        # Deduplicate by build_id
        unique_releases = {r.build_id: r for r in all_releases}
        
        # Update tracked data
        for release in unique_releases.values():
            self.tracked_data['builds'][release.build_id] = asdict(release)
        
        # Save tracking data
        self._save_tracked()
        
        return list(unique_releases.values())
    
    def generate_matrix(self, releases: List[WindowsRelease]) -> Dict:
        """
        Generate GitHub Actions matrix from releases
        
        Returns:
            Dictionary suitable for matrix strategy
        """
        matrix = {
            'include': []
        }
        
        for release in releases:
            # Generate matrix entries for different build types
            for build_type in ['standard', 'core', 'nano']:
                for edition in [1, 6]:  # Home, Pro
                    matrix['include'].append({
                        'version': release.version,
                        'build': release.build_number,
                        'iso_url': release.iso_url,
                        'build_type': build_type,
                        'edition': edition,
                        'edition_name': 'Home' if edition == 1 else 'Pro',
                        'title': release.title.replace(' ', '_').replace('(', '').replace(')', '')
                    })
        
        return matrix
    
    def create_github_issue(self, release: WindowsRelease) -> Dict:
        """
        Generate GitHub issue data for new release
        
        Returns:
            Dictionary with issue title and body
        """
        body = f"""## 🎉 New Windows Release Detected

**Build Information:**
- **Title:** {release.title}
- **Build Number:** {release.build_number}
- **Version:** {release.version}
- **Architecture:** {release.architecture}
- **Channel:** {release.channel}
- **Detection Date:** {release.detected_date}

**ISO Source:**
- {release.iso_url}

**Automated Actions:**
- [ ] Trigger Tiny11 Standard build
- [ ] Trigger Tiny11 Core build
- [ ] Trigger Nano11 build
- [ ] Test builds in VM
- [ ] Upload to SourceForge
- [ ] Update documentation

**Build Matrix:**
- Home Edition (Standard, Core, Nano)
- Pro Edition (Standard, Core, Nano)

---
*This issue was automatically created by the Version Matrix Builder*  
*Author: [kelexine](https://github.com/kelexine)*
"""
        
        return {
            'title': f"🆕 New Windows {release.version} Release - Build {release.build_number}",
            'body': body,
            'labels': ['automated', 'new-release', 'build-pending']
        }


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Windows 11 Release Detection System'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force check even if recently checked'
    )
    parser.add_argument(
        '--output',
        default='github_output.txt',
        help='GitHub Actions output file'
    )
    parser.add_argument(
        '--tracking-file',
        default='tracked_releases.json',
        help='Release tracking file'
    )
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = ReleaseDetector(tracking_file=args.tracking_file)
    
    # Detect new releases
    logger.info("🚀 Starting release detection...")
    new_releases = detector.detect_new_releases(force=args.force)
    
    if not new_releases:
        logger.info("📭 No new releases detected")
        
        # Write outputs for GitHub Actions
        with open(args.output, 'w') as f:
            f.write("has_new=false\n")
            f.write("new_releases=[]\n")
            f.write("releases_matrix={}\n")
        
        return 0
    
    # We found new releases!
    logger.info(f"✅ Found {len(new_releases)} new release(s)!")
    
    for release in new_releases:
        logger.info(f"  - {release.title} (Build {release.build_number})")
    
    # Generate matrix
    matrix = detector.generate_matrix(new_releases)
    
    # Write outputs for GitHub Actions
    with open(args.output, 'w') as f:
        f.write("has_new=true\n")
        f.write(f"new_releases={json.dumps([asdict(r) for r in new_releases])}\n")
        f.write(f"releases_matrix={json.dumps(matrix)}\n")
    
    logger.info("✅ Detection complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
