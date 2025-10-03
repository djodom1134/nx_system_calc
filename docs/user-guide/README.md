# Nx System Calculator - User Manual

**Version:** 1.0.0  
**Last Updated:** October 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using the Calculator](#using-the-calculator)
4. [Understanding Results](#understanding-results)
5. [Generating Reports](#generating-reports)
6. [Customization & Branding](#customization--branding)
7. [Multi-Site Deployments](#multi-site-deployments)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

### What is the Nx System Calculator?

The Nx System Calculator is a professional tool designed to help you accurately estimate hardware and storage requirements for Network Optix Video Management System (VMS) deployments. It calculates:

- **Server Requirements**: Number and specifications of servers needed
- **Storage Capacity**: Total storage required with RAID overhead
- **Network Bandwidth**: Average and peak bandwidth requirements
- **License Counts**: Number of camera licenses needed
- **Cost Estimates**: Approximate hardware costs

### Who Should Use This Tool?

- **Sales Engineers**: Create accurate quotes and proposals
- **System Integrators**: Design and scope VMS deployments
- **IT Managers**: Plan infrastructure requirements
- **Customers**: Understand system requirements before purchase

---

## Getting Started

### Accessing the Calculator

**Web Interface:**
- Development: `http://localhost:5173`
- Production: `https://your-domain.com`

**System Requirements:**
- Modern web browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled
- Minimum screen resolution: 1024x768

### Interface Overview

The calculator interface consists of four main sections:

1. **Project Information** - Basic project details
2. **Camera Configuration** - Camera groups and settings
3. **System Configuration** - Server and storage settings
4. **Results Panel** - Calculated requirements and recommendations

---

## Using the Calculator

### Step 1: Project Information

Enter basic project details:

**Required Fields:**
- **Project Name**: Descriptive name for your deployment (e.g., "Downtown Surveillance")
- **Created By**: Your name or company name
- **Email Address**: Contact email for reports

**Optional Fields:**
- **Company Name**: For branding on reports
- **Notes**: Additional project notes or requirements

**Example:**
```
Project Name: Downtown Office Complex
Created By: John Doe
Email: john.doe@acmesecurity.com
Company Name: Acme Security Solutions
```

---

### Step 2: Camera Configuration

Configure your camera groups. You can add multiple groups with different settings.

#### Adding a Camera Group

Click **"Add Camera Group"** to create a new group. Each group represents cameras with identical specifications.

#### Camera Group Parameters

**1. Number of Cameras**
- Range: 1 - 2560 cameras per site
- Enter the total number of cameras with these specifications
- **Tip**: Group cameras by similar resolution and recording settings

**2. Resolution**
- Select from 14 preset resolutions:
  - **VGA (640x480)** - 0.3 MP
  - **720p (1280x720)** - 0.9 MP
  - **1080p (1920x1080)** - 2 MP ⭐ Most common
  - **4MP (2688x1520)** - 4 MP
  - **5MP (2592x1944)** - 5 MP
  - **4K (3840x2160)** - 8 MP
  - **12MP (4000x3000)** - 12 MP
  - And more...

**Recommendation**: Use 1080p (2MP) for most applications. Higher resolutions increase storage and bandwidth significantly.

**3. Frame Rate (FPS)**
- Range: 1 - 60 frames per second
- Common values:
  - **15 FPS**: Low-traffic areas, parking lots
  - **30 FPS**: Standard surveillance ⭐ Recommended
  - **60 FPS**: High-speed events, casinos

**Tip**: Higher FPS increases storage linearly. 30 FPS uses 2x storage compared to 15 FPS.

**4. Codec**
- **H.264**: Industry standard, wide compatibility ⭐ Recommended
- **H.265 (HEVC)**: 30-50% better compression, requires more CPU
- **MJPEG**: Uncompressed, very high bandwidth
- **MPEG-4**: Legacy codec

**Recommendation**: Use H.264 for compatibility, H.265 for bandwidth-constrained sites.

**5. Quality**
- **Low**: Minimal detail, lowest storage
- **Medium**: Balanced quality and storage ⭐ Recommended
- **High**: Maximum detail, highest storage

**Impact**: Quality affects bitrate by 3-5x between Low and High.

**6. Recording Mode**
- **Continuous**: 24/7 recording ⭐ Most common
- **Motion Detection**: Records only when motion detected (30-50% storage savings)
- **Scheduled**: Custom recording schedule

**7. Audio**
- Enable if cameras have audio
- Adds ~64 kbps per camera
- Minimal storage impact

#### Example Camera Group

```
Camera Group 1: Main Entrances
- Cameras: 20
- Resolution: 1080p (2MP)
- FPS: 30
- Codec: H.264
- Quality: High
- Recording: Continuous
- Audio: Enabled

Camera Group 2: Parking Lots
- Cameras: 50
- Resolution: 1080p (2MP)
- FPS: 15
- Codec: H.264
- Quality: Medium
- Recording: Motion Detection
- Audio: Disabled
```

---

### Step 3: Storage & Retention

**Retention Period**
- Range: 1 - 365 days
- Common values:
  - **7 days**: Retail, low-risk areas
  - **30 days**: Standard commercial ⭐ Recommended
  - **90 days**: High-security, compliance requirements
  - **180+ days**: Banking, critical infrastructure

**Storage Impact**: Retention period directly multiplies storage requirements.

**Example**: 100 cameras at 30 days = 10 TB. Same cameras at 90 days = 30 TB.

---

### Step 4: Server Configuration

**RAID Type**
- **RAID 0**: No redundancy, maximum capacity (NOT RECOMMENDED)
- **RAID 1**: Mirror, 50% overhead, 1 drive fault tolerance
- **RAID 5**: Distributed parity, 33% overhead, 1 drive fault tolerance ⭐ Recommended
- **RAID 6**: Double parity, 50% overhead, 2 drive fault tolerance
- **RAID 10**: Mirror + Stripe, 50% overhead, high performance

**Recommendation**: RAID 5 for most deployments, RAID 6 for critical systems.

**Failover Configuration**
- **None**: No failover servers ⭐ Most common
- **N+1**: One additional server for failover (2x server count)
- **N+2**: Two additional servers for failover (3x server count)

**Network Interface**
- **NIC Capacity**: 1000 Mbps (1 Gbps) or 10000 Mbps (10 Gbps)
- **NIC Count**: Number of network interfaces per server

**Recommendation**: 1 Gbps for up to 200 cameras, 10 Gbps for larger deployments.

---

## Understanding Results

### Bandwidth Summary

**Average Bandwidth**
- Typical bandwidth during normal recording
- Used for network planning
- Includes 20% headroom for safety

**Peak Bandwidth**
- Maximum bandwidth during high-motion events
- Used for NIC capacity planning
- Critical for network switch sizing

**Example:**
```
Average Bandwidth: 245 Mbps
Peak Bandwidth: 294 Mbps
Required NICs: 1 x 1 Gbps
```

**Interpretation**: This deployment needs one 1 Gbps network interface. Peak usage is well below capacity.

---

### Storage Summary

**Total Storage Required**
- Raw storage needed before RAID overhead
- Based on bitrate × retention × cameras

**Usable Storage**
- Storage available after RAID overhead
- What you actually get for recordings

**RAID Overhead**
- Percentage lost to RAID parity/mirroring
- RAID 5: ~33%, RAID 6: ~50%, RAID 10: ~50%

**Example:**
```
Total Storage: 15.2 TB
Usable Storage: 10.1 TB
RAID Overhead: 33.6% (RAID 5)
```

**Interpretation**: You need 15.2 TB of physical drives to get 10.1 TB usable storage.

---

### Server Summary

**Required Server Count**
- Minimum servers needed for camera count
- Based on 256 cameras per server limit
- Multiplied by failover factor

**Recommended Specification**
- **Entry**: Up to 64 cameras, 4 cores, 16 GB RAM
- **Mid-Range**: Up to 128 cameras, 8 cores, 32 GB RAM ⭐ Most common
- **High-End**: Up to 256 cameras, 16 cores, 64 GB RAM
- **Enterprise**: 256+ cameras, 32 cores, 128 GB RAM

**Per-Server Load**
- Cameras per server
- Storage per server
- Bandwidth per server

**Example:**
```
Required Servers: 2
Recommended Spec: Mid-Range
Cameras per Server: 100
Storage per Server: 7.6 TB
Bandwidth per Server: 147 Mbps
```

---

### License Summary

**Total Licenses**
- One license per camera
- Distributed across servers

**Cost Estimate**
- Approximate hardware costs
- Does not include:
  - Software licenses
  - Installation labor
  - Network infrastructure
  - Cameras themselves

---

## Generating Reports

### Creating a PDF Report

1. Complete your calculation
2. Review results for accuracy
3. Click **"Generate PDF Report"**
4. Report downloads automatically

### Report Contents

**Page 1: Executive Summary**
- Project information
- Total requirements overview
- Cost estimate

**Page 2: Detailed Breakdown**
- Camera configuration table
- Bandwidth analysis
- Storage calculation
- Server specifications

**Page 3: Recommendations**
- Best practices
- Optimization suggestions
- Scalability considerations

**Page 4: Technical Specifications**
- Detailed server specs
- Network requirements
- RAID configuration

### Emailing Reports

1. Click **"Email Report"**
2. Enter recipient email and name
3. Add optional message
4. Click **"Send"**

**Features:**
- Professional branded email template
- PDF report attached
- Automatic BCC to sales team
- Delivery confirmation

---

## Customization & Branding

### OEM White-Labeling

Customize the calculator with your company branding:

**Upload Logo**
1. Click **"Upload Logo"** in settings
2. Select image file (PNG, JPG, SVG)
3. Maximum size: 5 MB
4. Recommended: 300x100 pixels, transparent background

**Brand Colors**
- Primary color for buttons and headers
- Hex color code (e.g., #0066CC)

**Company Information**
- Company name appears on reports
- Contact information in footer

**Custom Disclaimers**
- Add legal disclaimers to reports
- Customize terms and conditions

---

## Multi-Site Deployments

### Adding Multiple Sites

For deployments across multiple locations:

1. Calculate each site separately
2. Save each project with site name
3. Combine totals for procurement

**Site Limits:**
- Maximum 2560 cameras per site
- Maximum 10 servers per site

**Example Multi-Site:**
```
Site 1: Headquarters - 500 cameras, 2 servers
Site 2: Warehouse - 200 cameras, 1 server
Site 3: Retail Store - 100 cameras, 1 server
Total: 800 cameras, 4 servers
```

---

## Troubleshooting

### Common Issues

**Issue: "Too many cameras for single site"**
- **Cause**: Exceeded 2560 camera limit
- **Solution**: Split into multiple sites or reduce camera count

**Issue: "Insufficient network capacity"**
- **Cause**: Bandwidth exceeds NIC capacity
- **Solution**: Add more NICs or upgrade to 10 Gbps

**Issue: "Storage calculation seems high"**
- **Cause**: High resolution, FPS, or quality settings
- **Solution**: Review camera settings, consider H.265 codec, or motion detection

**Issue: "PDF generation failed"**
- **Cause**: Server error or timeout
- **Solution**: Refresh page and try again, contact support if persists

**Issue: "Email not received"**
- **Cause**: Spam filter or incorrect email
- **Solution**: Check spam folder, verify email address, download PDF directly

---

## FAQ

**Q: How accurate are the calculations?**
A: Calculations are based on Network Optix's proven formulas with 10+ years of field data. Accuracy is typically ±10% depending on actual scene complexity.

**Q: Can I save my calculations?**
A: Yes, click "Save Project" to store calculations. Retrieve them later from the Projects menu.

**Q: What if I need more than 2560 cameras?**
A: Create multiple site calculations. Each site supports up to 2560 cameras and 10 servers.

**Q: How do I choose between H.264 and H.265?**
A: H.265 saves 30-50% bandwidth/storage but requires newer cameras and more server CPU. Use H.264 for compatibility.

**Q: What retention period should I use?**
A: 30 days is standard for most commercial applications. Check local regulations for compliance requirements.

**Q: Can I customize the configuration presets?**
A: Yes, administrators can edit JSON configuration files. See Configuration Guide for details.

**Q: Is there an API for integration?**
A: Yes, full REST API available. See API Documentation for details.

**Q: What browsers are supported?**
A: Chrome, Firefox, Safari, and Edge (latest 2 versions). IE11 not supported.

---

## Getting Help

**Technical Support:**
- Email: support@networkoptix.com
- Phone: +1-555-NX-SUPPORT
- Hours: Monday-Friday, 9 AM - 5 PM EST

**Sales Inquiries:**
- Email: sales@networkoptix.com
- Phone: +1-555-NX-SALES

**Documentation:**
- User Manual: This document
- API Documentation: `/docs/api/`
- Configuration Guide: `/docs/configuration-guide.md`
- Deployment Guide: `/docs/deployment-guide.md`

---

**Copyright © 2025 Network Optix, Inc. All rights reserved.**

