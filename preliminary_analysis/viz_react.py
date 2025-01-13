import pandas as pd

def generate_html_visualization():
    """Generate a self-contained HTML visualization"""
    # Read the CSV data
    df = pd.read_csv('/Users/noamgal/Downloads/NUR/celular1819_v1.3/zone_time_profiles.csv')
    
    # Convert data to JSON for embedding
    json_data = df.to_json(orient='records')
    
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Temporal Trip Patterns</title>
    <meta charset="utf-8">
    <script src="https://unpkg.com/react@17.0.2/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@17.0.2/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/prop-types@15.8.1/prop-types.min.js"></script>
    <script src="https://unpkg.com/recharts@2.10.3/umd/Recharts.js"></script>
    <script src="https://unpkg.com/@babel/standalone@7.23.6/babel.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
            background: #111;
            color: #fff;
            font-size: 16px;
        }
        .card {
            background: #1a1a1a;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-width: 1400px;
            margin: 0 auto;
        }
        .title {
            text-align: center;
            margin-bottom: 30px;
            font-size: 36px;
            font-weight: bold;
        }
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
            margin-top: 40px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            font-size: 18px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
        }
        .legend-color {
            width: 18px;
            height: 18px;
            margin-right: 12px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot, Label } = Recharts;
        
        const data = DATA_PLACEHOLDER;

        // Process data and find peaks
        const formattedData = data.reduce((acc, row) => {
            const existingHour = acc.find(d => d.hour === row.hour);
            if (existingHour) {
                existingHour[`${row.zone_name}_arrivals`] = row.arrivals;
                existingHour[`${row.zone_name}_departures`] = row.departures;
            } else {
                acc.push({
                    hour: row.hour,
                    [`${row.zone_name}_arrivals`]: row.arrivals,
                    [`${row.zone_name}_departures`]: row.departures
                });
            }
            return acc;
        }, []);

        // Find peak values for annotations
        const findPeaks = () => {
            const peaks = {};
            ['Beer Sheva Innovation District', 'Matam Haifa'].forEach(zone => {
                const arrivals = formattedData.map(d => ({
                    hour: d.hour,
                    value: d[`${zone}_arrivals`]
                }));
                const departures = formattedData.map(d => ({
                    hour: d.hour,
                    value: d[`${zone}_departures`]
                }));
                
                peaks[zone] = {
                    arrivals: arrivals.reduce((max, curr) => curr.value > max.value ? curr : max),
                    departures: departures.reduce((max, curr) => curr.value > max.value ? curr : max)
                };
            });
            return peaks;
        };

        const peaks = findPeaks();

        const CustomTooltip = ({ active, payload, label }) => {
            if (active && payload && payload.length) {
                return (
                    <div style={{
                        background: 'rgba(26, 26, 26, 0.95)',
                        border: '1px solid #333',
                        padding: '16px',
                        borderRadius: '6px',
                        boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                        fontSize: '16px'
                    }}>
                        <p style={{ margin: '0 0 12px', fontWeight: 'bold', fontSize: '18px' }}>
                            {`${label}:00`}
                        </p>
                        {payload.map((entry, index) => {
                            const [zone, type] = entry.name.split('_');
                            return (
                                <p key={index} style={{ 
                                    margin: '6px 0',
                                    color: entry.color,
                                    fontSize: '16px'
                                }}>
                                    {zone.replace(/-/g, ' ')} {type}: {entry.value.toFixed(1)}%
                                </p>
                            );
                        })}
                    </div>
                );
            }
            return null;
        };

        const PeakLabel = ({ x, y, value, zone, type, color }) => (
            <g transform={`translate(${x},${y})`}>
                <text
                    x={0}
                    y={-20}
                    fill={color}
                    textAnchor="middle"
                    fontSize="16"
                >
                    {`${zone.split(' ')[0]} ${type}`}
                </text>
                <text
                    x={0}
                    y={-4}
                    fill={color}
                    textAnchor="middle"
                    fontSize="16"
                    fontWeight="bold"
                >
                    {`${value.toFixed(1)}%`}
                </text>
            </g>
        );

        const App = () => {
            return (
                <div className="card">
                    <h2 className="title">Daily Trip Patterns Comparison</h2>
                    <ResponsiveContainer width="100%" height={700}>
                        <LineChart
                            data={formattedData}
                            margin={{
                                top: 40,
                                right: 80,
                                left: 80,
                                bottom: 40
                            }}
                        >
                            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                            <XAxis 
                                dataKey="hour"
                                stroke="#fff"
                                tickFormatter={tick => `${tick}:00`}
                                label={{
                                    value: 'Hour of Day',
                                    position: 'bottom',
                                    fill: '#fff',
                                    offset: 20,
                                    fontSize: 24
                                }}
                                tick={{ fontSize: 18 }}
                            />
                            <YAxis
                                stroke="#fff"
                                label={{
                                    value: 'Percentage of Daily Trips',
                                    angle: -90,
                                    position: 'insideLeft',
                                    fill: '#fff',
                                    offset: -20,
                                    fontSize: 24
                                }}
                                tick={{ fontSize: 18 }}
                            />
                            <Tooltip content={<CustomTooltip />} />
                            
                            {Object.entries(peaks).map(([zone, peakData]) => (
                                <React.Fragment key={zone}>
                                    <ReferenceDot
                                        x={peakData.arrivals.hour}
                                        y={peakData.arrivals.value}
                                        r={6}
                                    >
                                        <PeakLabel
                                            value={peakData.arrivals.value}
                                            zone={zone}
                                            type="Arrivals"
                                            color={zone === 'Beer Sheva Innovation District' ? '#3498db' : '#e74c3c'}
                                        />
                                    </ReferenceDot>
                                    <ReferenceDot
                                        x={peakData.departures.hour}
                                        y={peakData.departures.value}
                                        r={6}
                                    >
                                        <PeakLabel
                                            value={peakData.departures.value}
                                            zone={zone}
                                            type="Departures"
                                            color={zone === 'Beer Sheva Innovation District' ? '#2980b9' : '#c0392b'}
                                        />
                                    </ReferenceDot>
                                </React.Fragment>
                            ))}
                            
                            {/* Beer Sheva Innovation District */}
                            <Line
                                type="monotone"
                                dataKey="Beer Sheva Innovation District_arrivals"
                                stroke="#3498db"
                                strokeWidth={3}
                                dot={false}
                                activeDot={{ r: 8 }}
                                name="Beer Sheva Arrivals"
                            />
                            <Line
                                type="monotone"
                                dataKey="Beer Sheva Innovation District_departures"
                                stroke="#2980b9"
                                strokeWidth={3}
                                strokeDasharray="5 5"
                                dot={false}
                                activeDot={{ r: 8 }}
                                name="Beer Sheva Departures"
                            />
                            
                            {/* Matam Haifa */}
                            <Line
                                type="monotone"
                                dataKey="Matam Haifa_arrivals"
                                stroke="#e74c3c"
                                strokeWidth={3}
                                dot={false}
                                activeDot={{ r: 8 }}
                                name="Matam Arrivals"
                            />
                            <Line
                                type="monotone"
                                dataKey="Matam Haifa_departures"
                                stroke="#c0392b"
                                strokeWidth={3}
                                strokeDasharray="5 5"
                                dot={false}
                                activeDot={{ r: 8 }}
                                name="Matam Departures"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                    
                    <div className="legend">
                        <div className="legend-item">
                            <div className="legend-color" style={{ background: '#3498db' }} />
                            <span>Beer Sheva Arrivals</span>
                        </div>
                        <div className="legend-item">
                            <div className="legend-color" style={{ background: '#2980b9' }} />
                            <span>Beer Sheva Departures</span>
                        </div>
                        <div className="legend-item">
                            <div className="legend-color" style={{ background: '#e74c3c' }} />
                            <span>Matam Arrivals</span>
                        </div>
                        <div className="legend-item">
                            <div className="legend-color" style={{ background: '#c0392b' }} />
                            <span>Matam Departures</span>
                        </div>
                    </div>
                </div>
            );
        };

        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>'''

    # Insert the data into the template
    html_content = html_content.replace('DATA_PLACEHOLDER', json_data)
    
    # Write the file
    output_path = '/Users/noamgal/Downloads/NUR/celular1819_v1.3/zone_time_profiles.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Visualization has been generated at: {output_path}")

if __name__ == "__main__":
    generate_html_visualization()