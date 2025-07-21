"""GZIP compression utilities for monitoring setup."""

import base64
import gzip


def create_compressed_monitoring_user_data(targets, alert_email=None, gmail_app_password=None):
    """Create GZIP COMPRESSED user data - BYPASSES 16KB LIMIT!"""
    
    targets_str = '", "'.join(targets)
    
    # FULL COMPREHENSIVE MONITORING SCRIPT - NO CUTS!
    full_monitoring_script = f"""#!/bin/bash
# COMPREHENSIVE MONITORING SETUP WITH GZIP COMPRESSION
yum update -y
yum install -y docker curl wget
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

mkdir -p /opt/monitoring
cd /opt/monitoring

# Docker Compose
cat > docker-compose.yml << 'EOF'
version: '3.8'
networks:
  monitoring:
    driver: bridge

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports: ["9090:9090"]
    volumes:
      - "./prometheus.yml:/etc/prometheus/prometheus.yml:ro"
    restart: unless-stopped
    networks: [monitoring]

  blackbox:
    image: prom/blackbox-exporter:latest
    container_name: blackbox
    ports: ["9115:9115"]
    volumes:
      - "./blackbox.yml:/etc/blackbox_exporter/config.yml:ro"
    restart: unless-stopped
    networks: [monitoring]

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports: ["3000:3000"]
    environment:
      - "GF_SECURITY_ADMIN_PASSWORD=admin123"
      - "GF_USERS_ALLOW_SIGN_UP=false"
      - "GF_SMTP_ENABLED={bool(alert_email)}"
      - "GF_SMTP_HOST=smtp.gmail.com:587"
      - "GF_SMTP_USER={alert_email or ''}"
      - "GF_SMTP_PASSWORD={gmail_app_password or ''}"
      - "GF_SMTP_FROM_ADDRESS={alert_email or 'noreply@localhost'}"
      - "GF_SMTP_FROM_NAME=Website Monitor"
    volumes:
      - "grafana_data:/var/lib/grafana"
      - "./grafana-provisioning:/etc/grafana/provisioning"
    restart: unless-stopped
    networks: [monitoring]
    depends_on: [prometheus]

volumes:
  grafana_data:
EOF

# Blackbox config
cat > blackbox.yml << 'EOF'
modules:
  http_2xx:
    prober: http
    timeout: 10s
    http:
      method: GET
      follow_redirects: true
      preferred_ip_protocol: "ip4"
EOF

# Prometheus config  
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets: ["{targets_str}"]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox:9115

  - job_name: 'blackbox_health'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets: [{", ".join([f'"{target}/health"' for target in targets])}]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox:9115
EOF

# Create Grafana provisioning
mkdir -p grafana-provisioning/datasources
mkdir -p grafana-provisioning/dashboards

# Datasource config
cat > grafana-provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    uid: prometheus
EOF

# Dashboard provisioning
cat > grafana-provisioning/dashboards/dashboards.yml << 'EOF'
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

# Create comprehensive dashboard 
cat > grafana-provisioning/dashboards/website-monitoring.json << 'EOF'
{{
  "annotations": {{
    "list": [
      {{
        "builtIn": 1,
        "datasource": {{
          "type": "grafana",
          "uid": "-- Grafana --"
        }},
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }}
    ]
  }},
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": null,
  "links": [],
  "liveNow": false,
  "panels": [
    {{
      "datasource": {{
        "type": "prometheus",
        "uid": "prometheus"
      }},
      "fieldConfig": {{
        "defaults": {{
          "color": {{
            "mode": "thresholds"
          }},
          "custom": {{
            "align": "center",
            "cellOptions": {{
              "type": "color-background"
            }},
            "inspect": false
          }},
          "mappings": [
            {{
              "options": {{
                "0": {{
                  "color": "red",
                  "index": 1,
                  "text": "DOWN"
                }},
                "1": {{
                  "color": "green", 
                  "index": 0,
                  "text": "UP"
                }}
              }},
              "type": "value"
            }}
          ],
          "thresholds": {{
            "mode": "absolute",
            "steps": [
              {{
                "color": "red",
                "value": null
              }},
              {{
                "color": "green",
                "value": 1
              }}
            ]
          }},
          "unit": "none"
        }},
        "overrides": []
      }},
      "gridPos": {{
        "h": 8,
        "w": 24,
        "x": 0,
        "y": 0
      }},
      "id": 1,
      "options": {{
        "showHeader": true
      }},
      "pluginVersion": "10.0.0",
      "targets": [
        {{
          "datasource": {{
            "type": "prometheus",
            "uid": "prometheus"
          }},
          "expr": "probe_success{{job=\\"blackbox\\"}}",
          "format": "table",
          "instant": true,
          "legendFormat": "{{{{instance}}}}",
          "refId": "A"
        }}
      ],
      "title": "Website Status",
      "transformations": [
        {{
          "id": "organize",
          "options": {{
            "excludeByName": {{
              "Time": true,
              "__name__": true,
              "job": true
            }},
            "renameByName": {{
              "Value": "Status",
              "instance": "Website"
            }}
          }}
        }}
      ],
      "type": "table"
    }},
    {{
      "datasource": {{
        "type": "prometheus",
        "uid": "prometheus"
      }},
      "fieldConfig": {{
        "defaults": {{
          "color": {{
            "mode": "palette-classic"
          }},
          "custom": {{
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {{
              "legend": false,
              "tooltip": false,
              "vis": false
            }},
            "lineInterpolation": "linear",
            "lineWidth": 2,
            "pointSize": 5,
            "scaleDistribution": {{
              "type": "linear"
            }},
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {{
              "group": "A",
              "mode": "none"
            }},
            "thresholdsStyle": {{
              "mode": "line"
            }}
          }},
          "mappings": [],
          "thresholds": {{
            "mode": "absolute",
            "steps": [
              {{
                "color": "green",
                "value": null
              }},
              {{
                "color": "yellow", 
                "value": 1000
              }},
              {{
                "color": "red",
                "value": 3000
              }}
            ]
          }},
          "unit": "ms"
        }},
        "overrides": []
      }},
      "gridPos": {{
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 8
      }},
      "id": 2,
      "options": {{
        "legend": {{
          "calcs": ["last", "mean", "max"],
          "displayMode": "table",
          "placement": "bottom"
        }},
        "tooltip": {{
          "mode": "multi",
          "sort": "none"
        }}
      }},
      "targets": [
        {{
          "datasource": {{
            "type": "prometheus",
            "uid": "prometheus"
          }},
          "expr": "probe_duration_seconds{{job=\\"blackbox\\"}} * 1000",
          "legendFormat": "{{{{instance}}}}",
          "refId": "A"
        }}
      ],
      "title": "Response Time",
      "type": "timeseries"
    }},
    {{
      "datasource": {{
        "type": "prometheus",
        "uid": "prometheus"
      }},
      "fieldConfig": {{
        "defaults": {{
          "color": {{
            "mode": "thresholds"
          }},
          "mappings": [
            {{
              "options": {{
                "0": {{
                  "color": "red",
                  "index": 1,
                  "text": "FAILED"
                }},
                "1": {{
                  "color": "green",
                  "index": 0,
                  "text": "HEALTHY"
                }}
              }},
              "type": "value"
            }}
          ],
          "thresholds": {{
            "mode": "absolute",
            "steps": [
              {{
                "color": "red",
                "value": null
              }},
              {{
                "color": "green",
                "value": 1
              }}
            ]
          }},
          "unit": "none"
        }},
        "overrides": []
      }},
      "gridPos": {{
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 8
      }},
      "id": 3,
      "options": {{
        "colorMode": "background",
        "graphMode": "area",
        "justifyMode": "center",
        "orientation": "horizontal",
        "reduceOptions": {{
          "calcs": ["lastNotNull"],
          "fields": "",
          "values": false
        }},
        "textMode": "auto"
      }},
      "pluginVersion": "10.0.0",
      "targets": [
        {{
          "datasource": {{
            "type": "prometheus",
            "uid": "prometheus"
          }},
          "expr": "probe_success{{job=\\"blackbox_health\\"}}",
          "legendFormat": "{{{{instance}}}}",
          "refId": "A"
        }}
      ],
      "title": "Health Check Status",
      "type": "stat"
    }}
  ],
  "refresh": "30s",
  "schemaVersion": 37,
  "style": "dark",
  "tags": ["monitoring"],
  "templating": {{
    "list": []
  }},
  "time": {{
    "from": "now-1h",
    "to": "now"
  }},
  "timepicker": {{}},
  "timezone": "",
  "title": "Website Monitoring Dashboard",
  "uid": "website-monitoring-dashboard",
  "version": 1,
  "weekStart": ""
}}
EOF

# Start services
echo "Starting monitoring services..."
docker-compose up -d

# Wait for services
echo "Waiting for services to initialize..."
sleep 120

# Configure Grafana alerts via API
if [ "{bool(alert_email)}" == "True" ] && [ -n "{alert_email or ''}" ]; then
    echo "Configuring Grafana email alerts..."
    
    # Wait for Grafana to be ready
    until curl -s http://localhost:3000/api/health > /dev/null; do
        echo "Waiting for Grafana..."
        sleep 10
    done
    
    # Create contact point
    curl -X POST http://admin:admin123@localhost:3000/api/v1/provisioning/contact-points \\
        -H 'Content-Type: application/json' \\
        -d '{{
            "name": "email-alerts",
            "type": "email",
            "settings": {{
                "addresses": "{alert_email or ''}"
            }}
        }}' || echo "Contact point creation attempted"
    
    # Create notification policy
    curl -X PUT http://admin:admin123@localhost:3000/api/v1/provisioning/policies \\
        -H 'Content-Type: application/json' \\
        -d '{{
            "receiver": "email-alerts",
            "group_by": ["grafana_folder", "alertname"],
            "routes": [
                {{
                    "receiver": "email-alerts",
                    "group_by": ["alertname"],
                    "matchers": [["alertname", "=", "WebsiteDown"]]
                }}
            ]
        }}' || echo "Policy creation attempted"
    
    # Create alert rule
    curl -X POST http://admin:admin123@localhost:3000/api/v1/provisioning/alert-rules \\
        -H 'Content-Type: application/json' \\
        -d '{{
            "uid": "website-down-alert",
            "title": "Website Down Alert",
            "condition": "C",
            "data": [
                {{
                    "refId": "A",
                    "queryType": "",
                    "relativeTimeRange": {{
                        "from": 300,
                        "to": 0
                    }},
                    "datasourceUid": "prometheus",
                    "model": {{
                        "expr": "probe_success{{job=\\\\"blackbox\\\\"}}",
                        "refId": "A"
                    }}
                }},
                {{
                    "refId": "C",
                    "queryType": "",
                    "relativeTimeRange": {{
                        "from": 0,
                        "to": 0
                    }},
                    "datasourceUid": "__expr__",
                    "model": {{
                        "expression": "A < 1",
                        "refId": "C",
                        "type": "threshold"
                    }}
                }}
            ],
            "noDataState": "NoData",
            "execErrState": "Alerting",
            "for": "2m",
            "annotations": {{
                "description": "Website {{{{ $labels.instance }}}} is down",
                "summary": "Website Down"
            }},
            "labels": {{
                "severity": "critical"
            }},
            "folderUID": ""
        }}' || echo "Alert rule creation attempted"
        
    echo "Email alert configuration completed!"
fi

# Get public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ip-v4)

echo "=== MONITORING SETUP COMPLETE ==="
echo "Grafana: http://$PUBLIC_IP:3000 (admin/admin123)"
echo "Prometheus: http://$PUBLIC_IP:9090"
echo "Dashboard: Working with UP/DOWN status and response times"
if [ "{bool(alert_email)}" == "True" ]; then
    echo "Email alerts: Configured for {alert_email or 'N/A'}"
fi
echo "Monitoring {len(targets)} website(s)"
echo "=================================="

# Final status
docker-compose ps
"""

    # COMPRESS THE FULL SCRIPT WITH GZIP
    compressed_data = gzip.compress(full_monitoring_script.encode('utf-8'))
    
    # Calculate compression statistics
    original_size = len(full_monitoring_script.encode('utf-8'))
    compressed_size = len(compressed_data)
    compression_ratio = (compressed_size / original_size) * 100
    
    print(f"GZIP Compression Stats:")
    print(f"   Original: {original_size:,} bytes ({original_size/1024:.1f} KB)")
    print(f"   Compressed: {compressed_size:,} bytes ({compressed_size/1024:.1f} KB)")
    print(f"   Ratio: {compression_ratio:.1f}%")
    print(f"   Saved: {original_size - compressed_size:,} bytes")
    
    if compressed_size > 16384:
        print(f"Warning: Still {compressed_size - 16384} bytes over 16KB limit!")
    else:
        print(f"FITS within 16KB AWS limit!")
    
    return base64.b64encode(compressed_data).decode()
 
