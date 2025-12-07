import { Stack, Box, Typography } from "@mui/material";
import {
	Area,
	AreaChart,
	Legend,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";
import MUIRechartsTooltip from "./Tooltip";

const MUILegend = (props) => {
	const { payload } = props;

	return (
		<Stack direction="row" spacing={2} alignItems="center" sx={{ mt: 1, paddingTop: "10px" }}>
			{payload.map((entry) => (
				<Stack
					key={entry.value}
					direction="row"
					spacing={1}
					alignItems="center"
				>
					<Box
						sx={{
							width: 12,
							height: 12,
							borderRadius: "20%",
							backgroundColor: entry.color,
						}}
					/>
					<Typography variant="body2">
						{entry.value.split("_")[0].toUpperCase()}
					</Typography>
				</Stack>
			))}
		</Stack>
	);
};

const SystemInfoChart = ({ series, colorScheme }) => {
	// Light theme uses indigo/purple, dark theme uses orange/red
	const cpuColor = colorScheme === 'light' ? '#8b5cf6' : '#e88c30'; // Violet for light, orange for dark
	const ramColor = colorScheme === 'light' ? '#6366f1' : '#dc2828'; // Indigo for light, red for dark

	return (
		<ResponsiveContainer width="100%" aspect={1.618} maxHeight={175}>
			<AreaChart data={series}>
				<XAxis
					dataKey="timeStep"
					type="number"
					domain={[-50, 0]}
					ticks={[-50, -40, -30, -20, -10, 0]}
					tickFormatter={(v) => `${v}s`}
					axisLine={false}
					tickLine={false}
					height={15}
					tick={{
						fontSize: 12,
						fontFamily: "Inter, sans-serif",
						fill: "#999",
						fontWeight: 500,
					}}
				/>
				<YAxis
					type="number"
					domain={[0, 100]}
					tickFormatter={(v) => `${v}%`}
					axisLine={false}
					tickLine={false}
					width={35}
					tick={{
						fontSize: 12,
						fontFamily: "Inter, sans-serif",
						fill: "#999",
						fontWeight: 500,
					}}
				/>

				<Tooltip formatter={(v) => `${v}%`} content={MUIRechartsTooltip} />

				<Area
					type="basis"
					dataKey="cpu_percent"
					stroke={cpuColor}
					fill={cpuColor}
					isAnimationActive={false}
				/>

				<Area
					type="basis"
					dataKey="ram_percent"
					stroke={ramColor}
					fill={ramColor}
					isAnimationActive={false}
				/>

				<Legend
					verticalAlign="bottom"
					horizontalAlign="middle"
					content={MUILegend}
					wrapperStyle={{
						width: "100%",
						display: "flex",
						justifyContent: "center",
					}}
				/>
			</AreaChart>
		</ResponsiveContainer>
	);
};

export default SystemInfoChart;

