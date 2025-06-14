
# Volumes by pluttan 
Simple app for beauty output of shell script.

```sh
wget https://clck.ru/3McCpj && chmod +x volumes.sh && ./volumes.sh <your script>.sh
```

## 📦 Installation  

Download with tiny url:
```sh
wget https://clck.ru/3McCpj && chmod +x volumes.sh
```

Download with checksum verification:
```sh
wget https://raw.githubusercontent.com/pluttan/volumes/main/volumes.sh && \
wget https://raw.githubusercontent.com/pluttan/volumes/main/volumes.sha256 && \
sha256sum -c volumes.sha256 && \
chmod +x volumes.sh
```

## 🚀 Usage  
```sh
./volumes.sh your-script.sh  # Show colored output
```

## 📝 Syntax Guide  

### Execution Modes  
| Syntax | Behavior |  
|--------|----------|  
| `command` | Runs in background (no output) |  
| `command # Message` | Foreground with critical failure |  
| `command ## Message` | Foreground with non-critical failure |  

### Status Indicators  
- `[WAIT]` - Command in progress  
- `[OK]` - Command succeeded  
- `[WARN]` - Non-critical failure (##)  
- `[ERROR]` - Critical failure (#)  
- `[INFO]` - Information by volumes

## 💡 Examples  

### Basic Example  
**Input script (`demo.sh`):**  
```sh
echo "Preparing..." # Initial setup
apt-get update ## System update
rm temp_file || false # Cleanup
{ echo "Step 1"; sleep 1; echo "Step 2"; } # Complex operation
```

**Output:**  
```
[OK] Initial setup
[WARN] System update - apt-get failed (1)
[ERROR] Cleanup - rm failed (1)
```

### Advanced Features  
```sh
# Multi-command blocks
{
  echo "Phase 1" &&
  docker build . &&
  echo "Done"
} # Build process
```