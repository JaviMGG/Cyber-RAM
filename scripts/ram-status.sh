#!/usr/bin/env bash
#
# ram-status.sh
# Lee el uso de RAM real del sistema (/proc/meminfo via `free`) y
# emite un JSON compatible con el módulo "custom" de Waybar.
#
# Salida: {"text":"...", "tooltip":"...", "class":"...", "percentage":N}

set -euo pipefail

WARN_THRESHOLD=60
CRIT_THRESHOLD=80

read -r total used _ _ _ available < <(free -b | awk '/^Mem:/{print $2,$3,$4,$5,$6,$7}')

total_gb=$(awk "BEGIN{printf \"%.1f\", $total/1024/1024/1024}")
used_gb=$(awk "BEGIN{printf \"%.1f\", $used/1024/1024/1024}")
free_gb=$(awk "BEGIN{printf \"%.1f\", $available/1024/1024/1024}")
pct=$(awk "BEGIN{printf \"%d\", ($used/$total)*100}")

tooltip="RAM TOTAL: ${total_gb} GB\nUSADA: ${used_gb} GB\nDISPONIBLE: ${free_gb} GB\nUSO: ${pct}%"

if   [ "$pct" -ge "$CRIT_THRESHOLD" ]; then css_class="critical"
elif [ "$pct" -ge "$WARN_THRESHOLD" ]; then css_class="warning"
else                                        css_class="normal"
fi

printf '{"text":"%s%% | %s/%s GB","tooltip":"%s","class":"%s","percentage":%s}\n' \
  "$pct" "$used_gb" "$total_gb" "$tooltip" "$css_class" "$pct"
