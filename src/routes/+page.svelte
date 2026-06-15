<script>
    import { Chart } from 'svelte-echarts'

    import { init, use } from 'echarts/core'
    import { LineChart } from 'echarts/charts'
    import { GridComponent, GeoComponent, TooltipComponent, LegendComponent } from 'echarts/components'
    import { CanvasRenderer } from 'echarts/renderers'
    
    // now with tree-shaking
    use([LineChart, GridComponent, CanvasRenderer, TooltipComponent, LegendComponent])

    let { data } = $props(); 
    let now = new Date();
    let MW_TO_GW = 1000;

    function utcToUK(utcString) {
        const utcDate = new Date(
            utcString.replace(' ', 'T') + ':00Z'
        );

        return utcDate.toLocaleString('en-GB', {
            timeZone: 'Europe/London',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }).replace(/^(\d{2})\/(\d{2})\/(\d{4}),\s*/, '$3-$2-$1 ');
    }

    const filterByCategory = (cat, conv=1) => data?.metrics?.filter(a => a.category === cat).map(a => [utcToUK(a.timestamp), a.value / conv]);

    let market_price_data = filterByCategory('market_price');
    let agile_price_data = filterByCategory('octopus_agile');
    let price_chart_options = {
        tooltip: {
            trigger: "axis",
            formatter: function (params) {
                let text = params[0].axisValueLabel + "<br>";
                params.forEach(p => {
                    text += `${p.marker} ${p.seriesName}: ${p.value[1].toFixed(3)} £/kWh<br>`;
                });
                return text;
            }
        },
        legend: {
            data: ["Wholesale Market", "Octopus Agile"],
        },
        xAxis: {
            type: "time",
            axisLabel: {
                hideOverlap: true,
                rotate: 45
            }
        },
        yAxis: {
            type: "value",
        },
        series: [
            {
                name: "Wholesale Market",
                data: market_price_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Octopus Agile",
                data: agile_price_data,
                type: "line",
                smooth: true,
            }
        ]
    };

    let demand_data = filterByCategory('demand', MW_TO_GW);

    
    let biomass_data = filterByCategory('Biomass', MW_TO_GW);
    let gas_data = filterByCategory('Fossil Gas', MW_TO_GW);
    let coal_data = filterByCategory('Fossil Hard coal', MW_TO_GW);
    let oil_data = filterByCategory('Fossil Oil', MW_TO_GW);
    let hydro_data = filterByCategory('Hydro Run-of-river and poundage', MW_TO_GW);
    let nuclear_data = filterByCategory('Nuclear', MW_TO_GW);
    let solar_data = filterByCategory('Solar', MW_TO_GW);
    let offshore_wind_data = filterByCategory('Wind Offshore', MW_TO_GW);
    let onshore_wind_data = filterByCategory('Wind Onshore', MW_TO_GW);
    let total_wind_data = Object.entries([...offshore_wind_data,...onshore_wind_data].reduce((a, [timestamp, value]) => {
        a[timestamp] = (a[timestamp] || 0) + value;
        return a;}, {})
        ).map(([timestamp, value]) => [timestamp, value]);
    let gen_chart_options = {
        tooltip: {
            trigger: "axis",
            formatter: function (params) {
                let text = params[0].axisValueLabel + "<br>";
                params.forEach(p => {
                    text += `${p.marker} ${p.seriesName}: ${p.value[1].toFixed(2)} GW<br>`;
                });
                return text;
            }
        },
        legend: {
            data: ["Biomass", "Gas", "Coal", "Oil", "Hydro", "Nuclear", "Solar", "Wind"]
        },
        xAxis: {
            type: "time",
            axisLabel: {
                hideOverlap: true,
                rotate: 45
            }
        },
        yAxis: {
            type: "value",
        },
        series: [
            {
                name: "Biomass",
                data: biomass_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Gas",
                data: gas_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Coal",
                data: coal_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Oil",
                data: oil_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Hydro",
                data: hydro_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Nuclear",
                data: nuclear_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Solar",
                data: solar_data,
                type: "line",
                smooth: true,
            },
            {
                name: "Wind",
                data: total_wind_data,
                type: "line",
                smooth: true
            }
        ]
    };

    let inter_map_options = {
        geo: {
            map: 'europe'
        },
        tooltip: {},
        visualMap: [
            {
                orient: 'horizontal'
            }
        ]
    };



</script>

<main class="dashboard-container">
    <div class="card info" id="time">
        <p>{now.toLocaleString('en-GB',{timeZone:'Europe/London', }).substring(0,17)}</p>
    </div>
    <div class="card info" id="demand">
        <p>Demand: {demand_data[demand_data.length - 1][1]} GW at {demand_data[demand_data.length - 1][0].substring(10,16)}</p>
    </div>
    <div class="card info" id="generation">
        <p>Generation:</p>
    </div>
    <div class="card chart" id="price-chart">
        <h3>Electricity Price £ / kWh</h3>
        <div class="chart-area">
            <Chart {init} options={price_chart_options} />
        </div>
    </div>
    <div class="card chart" id="generation-chart">
        <h3>Electricity Generation by Type / GW</h3>
        <div class="chart-area">
            <Chart {init} options={gen_chart_options} />
        </div>
    </div>
    <div class="card chart" id="interconnector-map">
        <h3>Interconnectors</h3>
        <div class="chart-area">
            
        </div>
    </div>
</main>

<style>
.dashboard-container {
  margin: 2rem 5rem;
  display: grid;
  gap: 0.5rem;
  font-family: sans-serif;
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.card {
  padding: 0.25rem 0 1rem 1.5rem;
  background-color: #fff;
  border-radius: 10px;
  min-width: 0;
}

.info {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0 0 0 0;
}

#time {
  grid-column: 1 / 2;
}

#demand {
  grid-column: 2 / 4;
}

#generation {
    grid-column: 4 / -1;
}

#price-chart {
  grid-column: 1 / 4;
}

#generation-chart {
  grid-column: 4 / -1;
}

.chart {
  min-width: 0;
}

.chart-area {
  height: 35rem;
  width: 100%;
}

@media (max-width: 1250px) {
  .dashboard-container {
    margin: 2rem 0.5rem;
    grid-template-columns: 1fr 1fr;
  }

  #time {
    grid-column: 1;
  }
  #demand {
    grid-column: 2 / -1;
  }
  #generation,
  #price-chart,
  #generation-chart {
    grid-column: 1 / -1;
  }
}

@media (max-width: 550px) {
  .dashboard-container {
    margin: 2rem 0.5rem;
    grid-template-columns: 1fr;
  }

  #time {
    grid-column: 1;
  }
  #demand {
    grid-column: 1;
  }
  #generation,
  #price-chart,
  #generation-chart {
    grid-column: 1 / -1;
  }
}

</style>