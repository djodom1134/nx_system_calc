# Configuration Files

This directory contains critical configuration files for the Nx System Calculator.

## ⚠️ **DEPLOYMENT CRITICAL**

**These files MUST be deployed with the application!**

Without these files, the API will return 500 errors and the application will not function.

---

## 📁 **Required Files**

### **1. resolutions.json**
Defines available camera resolutions and their properties.

**Fields:**
- `id` - Unique identifier (e.g., "1080p", "4k")
- `name` - Display name
- `width` - Horizontal pixels
- `height` - Vertical pixels
- `megapixels` - Total megapixels
- `common_fps` - Typical frame rates for this resolution

### **2. codecs.json**
Defines video codec configurations and compression ratios.

**Fields:**
- `id` - Unique identifier (e.g., "h264", "h265")
- `name` - Display name
- `compression_ratio` - Compression efficiency
- `quality_factor` - Quality multiplier
- `cpu_load` - Relative CPU usage
- `recommended` - Whether this codec is recommended

### **3. raid_types.json**
Defines RAID configurations and storage efficiency.

**Fields:**
- `id` - Unique identifier (e.g., "raid5", "raid6")
- `name` - Display name
- `description` - Description of RAID type
- `usable_percentage` - Percentage of raw storage that's usable
- `min_drives` - Minimum number of drives required
- `fault_tolerance` - Number of drive failures that can be tolerated
- `read_performance` - Read performance multiplier
- `write_performance` - Write performance multiplier
- `recommended` - Whether this RAID type is recommended
- `notes` - Additional information

### **4. server_specs.json**
Defines server hardware specifications and capabilities.

**Fields:**
- `cpu` - CPU specifications and performance tiers
- `memory` - RAM requirements and recommendations
- `storage` - Storage drive specifications
- `network` - Network interface specifications

---

## 🔧 **Deployment Instructions**

### **Option 1: Default Location (Recommended)**

Place the `config/` directory at the project root:

```
nx_system_calc/
├── backend/
├── frontend/
└── config/          ← Config files here
    ├── resolutions.json
    ├── codecs.json
    ├── raid_types.json
    └── server_specs.json
```

### **Option 2: Custom Location**

If deploying config files to a different location, set the `CONFIG_DIR` environment variable:

```bash
export CONFIG_DIR=/path/to/config
```

Or in `.env` file:
```
CONFIG_DIR=/path/to/config
```

---

## ✅ **Verification**

After deployment, verify config files are accessible:

```bash
# Run the deployment test script
cd backend
python3 test_deployment.py
```

Or test via API:
```bash
curl http://localhost:8000/api/v1/config/raid-types
curl http://localhost:8000/api/v1/config/codecs
curl http://localhost:8000/api/v1/config/resolutions
```

---

## 🐛 **Troubleshooting**

### **500 Error on Config Endpoints**

**Symptoms:**
```
GET /api/v1/config/raid-types - 500 (Internal Server Error)
```

**Solutions:**

1. **Verify files exist:**
   ```bash
   ls -la config/
   ```

2. **Check file permissions:**
   ```bash
   chmod 644 config/*.json
   ```

3. **Validate JSON syntax:**
   ```bash
   python3 -m json.tool config/raid_types.json
   python3 -m json.tool config/codecs.json
   python3 -m json.tool config/resolutions.json
   python3 -m json.tool config/server_specs.json
   ```

4. **Set CONFIG_DIR explicitly:**
   ```bash
   export CONFIG_DIR=/absolute/path/to/config
   ```

5. **Check backend logs** for detailed error messages

---

## 📝 **Modifying Configuration**

### **Adding a New RAID Type**

1. Edit `raid_types.json`
2. Add new entry to the `raid_types` array:
   ```json
   {
     "id": "custom_raid",
     "name": "Custom RAID",
     "description": "Custom RAID configuration",
     "usable_percentage": 75,
     "min_drives": 3,
     "fault_tolerance": 1,
     "read_performance": "1x",
     "write_performance": "1x",
     "recommended": true,
     "notes": "Custom notes"
   }
   ```
3. Validate JSON syntax
4. Restart the backend server

### **Adding a New Resolution**

1. Edit `resolutions.json`
2. Add new entry to the `resolutions` array
3. Validate JSON syntax
4. Restart the backend server

### **Adding a New Codec**

1. Edit `codecs.json`
2. Add new entry to the `codecs` array
3. Validate JSON syntax
4. Restart the backend server

---

## 🔒 **File Permissions**

Recommended permissions:
```bash
chmod 644 config/*.json  # Read-only for application
```

The application only needs **read** access to these files.

---

## 📚 **See Also**

- [DEPLOYMENT.md](../DEPLOYMENT.md) - Full deployment guide
- [backend/test_deployment.py](../backend/test_deployment.py) - Deployment verification script

