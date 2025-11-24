import PropTypes from "prop-types";
import { Paper, Typography, Box, Divider } from "@mui/material";

export default function MUIRechartsTooltip({
  active,
  payload,
  label,
  formatter,
  sx,
}) {
  if (!active || !payload || payload.length === 0) return null;
  const items = Array.isArray(payload) ? payload : [payload];

  return (
    <Paper
      elevation={3}
      sx={{ p: 1, minWidth: 150, pointerEvents: "none", ...sx }}
    >
      {label != null && (
        <Typography variant="caption" sx={{ opacity: 0.85, fontWeight:600, fontSize:"14px",  }} gutterBottom>
          {label}s
        </Typography>
      )}

      {items.map((row, i) => {

        const name = row.name ?? row.dataKey ?? `series-${i}`;
        const rawValue =
          row.value ?? (row.payload && row.payload[row.dataKey]) ?? null;
        const display =
          typeof formatter === "function"
            ? formatter(rawValue, name, row)
            : rawValue;
        const color =
          row.color ??
          (row.payload && row.payload.color) ??
          row.stroke ??
          undefined;

        return (
          <Box
            key={i}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent:"space-between",
              mb: i === items.length - 1 ? 0 : 0.5,
              gap: 1,
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Box
                sx={{
                    width: 12,
                    height: 12,
                    borderRadius: "20%",
                    backgroundColor: color,
                    }}
                    />
                <Typography
                variant="body2"
                noWrap
                sx={{ fontSize: "12px", fontWeight: 600, opacity: 0.75 }}
                >
                {String(name).split("_")[0].toUpperCase()}
                </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              {display == null ? "-" : String(display)}
            </Typography>
          </Box>
        );
      })}
    </Paper>
  );
}

MUIRechartsTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  formatter: PropTypes.func,
  sx: PropTypes.object,
};
