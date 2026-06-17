<script>
    import { Chart } from 'svelte-echarts';
    import { onMount } from 'svelte';
    import { init, use, registerMap } from 'echarts/core';
    import { LineChart, PieChart, MapChart } from 'echarts/charts';
    import { GraphicComponent, GridComponent, GeoComponent, VisualMapComponent, TooltipComponent, LegendComponent } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';
    import europeGeoJSON from '$lib/assets/europe.geojson?raw';
    
    // now with tree-shaking
    use([LineChart, PieChart,MapChart, GraphicComponent, GridComponent, CanvasRenderer, GeoComponent, VisualMapComponent, TooltipComponent, LegendComponent])

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
    let total_generation_data = biomass_data[biomass_data.length-1][1] + gas_data[gas_data.length-1][1] + coal_data[coal_data.length-1][1] + 
    oil_data[oil_data.length-1][1] + hydro_data[hydro_data.length-1][1] + nuclear_data[nuclear_data.length-1][1] + solar_data[solar_data.length-1][1] + 
    total_wind_data[total_wind_data.length-1][1];
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
                name: "Coal",
                data: coal_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Oil",
                data: oil_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Biomass",
                data: biomass_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Nuclear",
                data: nuclear_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Gas",
                data: gas_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Hydro",
                data: hydro_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Solar",
                data: solar_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Wind",
                data: total_wind_data,
                type: "line",
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            }
        ]
    };  

    let gen_pie_options = {
        graphic : [
            {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: `${total_generation_data.toFixed(2)} GW`,
                    textAlign: 'center',
                    fontSize: 20,
                    fontWeight: 'bold'
                }
            }
        ],
        tooltip: {
            trigger: 'item',
            formatter: function (params) {
                console.log(params);
                return params.name + ': ' + params.value.toFixed(2).toString() + ' GW (' + params.percent.toFixed(1) + '%)';
            }
        },
        legend: {
            top: '5%',
            left: 'center'
        },
        series: [
            {
                name: 'Access From',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                },
                emphasis: {
                        label: {
                        show: false
                    }
                },
                labelLine: {
                    show: false
                },
                data: [
                    { value: coal_data[coal_data.length - 1][1], name: 'Coal' },
                    { value: oil_data[oil_data.length - 1][1], name: 'Oil' },
                    { value: biomass_data[biomass_data.length - 1][1], name: 'Biomass' },
                    { value: nuclear_data[nuclear_data.length - 1][1], name: 'Nuclear' },
                    { value: gas_data[gas_data.length - 1][1], name: 'Gas' },
                    { value: hydro_data[hydro_data.length - 1][1], name: 'Hydro'},
                    { value: solar_data[solar_data.length - 1][1], name: 'Solar' },
                    { value: total_wind_data[total_wind_data.length - 1][1], name: 'Wind' },
                ]
            }
        ]
    }

    const europeJSON = JSON.parse(europeGeoJSON);
    registerMap('europe', europeJSON);
    let IEgreenlink = filterByCategory("Ireland (Greenlink)");
    let IEeastwest = filterByCategory("Ireland(East-West)");
    let IEinter = IEgreenlink[0][1] + IEeastwest[0][1];
    let FRIFA = filterByCategory("France(IFA)")
    let FRIFAtwo = filterByCategory("IFA2 (INTIFA2)")
    let FReleclink = filterByCategory("Eleclink (INTELEC)")
    let FRinter = FRIFA[0][1] + FRIFAtwo[0][1] + FReleclink[0][1];
    let NOnsl = filterByCategory("North Sea Link (INTNSL)")
    let NOinter = NOnsl[0][1];
    let DNviking = filterByCategory("Denmark (Viking link)")
    let DNinter = DNviking[0][1];
    let NLbritned = filterByCategory("Netherlands(BritNed)")
    let NLinter = NLbritned[0][1];
    let BEnemo = filterByCategory("Belgium (Nemolink)");
    let BEinter = BEnemo[0][1];
    let total_importexport = IEinter + FRinter + NOinter + DNinter + NLinter + BEinter;

    let inter_map_options = {
    geo: {
        map: 'europe',
        roam: false,
        boundingCoords: [
            [-5, 40],
            [0, 64]
        ],
        layoutCenter: ['50%','50%'],
        layoutsize: 800,
        aspectScale: 0.9,        // < 1 compresses vertically, > 1 horizontally
        nameProperty: 'NAME',
        label: { show: false },
        emphasis: { label: { show: false } }
    },
    tooltip: {
        formatter: function (params) {
                return params.name + ': ' + (params.value / 1000).toFixed(2).toString() + ' GW';
            }
    },
    visualMap: [
        {
        orient: 'horizontal',
        left: 0,
        bottom: 0,
        min: -Math.max(FRinter, IEinter, NLinter, NOinter, DNinter, BEinter),
        max: Math.max(FRinter, IEinter, NLinter, NOinter, DNinter, BEinter),
        inRange: { color: ['#FF4242','#FFFFFF', '#A7FF5C'] }
        }
    ],
    series: [
        {
        type: 'map',
        geoIndex: 0,
        name: 'Transfer',
        data: [
            { name: 'France', value: FRinter },
            { name: 'Ireland', value: IEinter },
            { name: 'Netherlands', value: NLinter },
            { name: 'Norway', value: NOinter },
            { name: 'Denmark', value: DNinter },
            { name: 'Belgium', value: BEinter }
        ]
        }
    ]
    };


</script>

<main class="dashboard-container">
    <div class="card info" id="time">
        <p>{now.toLocaleString('en-GB',{timeZone:'Europe/London', }).substring(0,17)}</p>
    </div>
    <div class="card info" id="demand">
        <p>Demand: {demand_data[demand_data.length - 1][1].toFixed(2)} GW at {demand_data[demand_data.length - 1][0].substring(10,16)}</p>
    </div>
    <div class="card info" id="generation">
        <p>Generation: {total_generation_data.toFixed(2)} GW + Imports/Exports: {(total_importexport/1000).toFixed(2)} GW = {(total_generation_data + total_importexport/1000).toFixed(2)} GW</p>
    </div>
    <div class="card chart" id="generation-pie">
        <h3>Generation by Source</h3>
        <div class="chart-area">
            <Chart {init} options={gen_pie_options} />
        </div>
    </div>
    <div class="card chart" id="generation-chart">
        <h3>Electricity Generation by Type / GW</h3>
        <div class="chart-area">
            <Chart {init} options={gen_chart_options} />
        </div>
    </div>
    <div class="card chart" id="interconnector-map">
        <h3>Imports / Exports (as of {FReleclink[FReleclink.length - 1][0].substring(10,16)})</h3>
        <div class="chart-area">
            <Chart {init} options={inter_map_options} />
        </div>
    </div>
    <div class="card chart" id="price-chart">
        <h3>Electricity Price £ / kWh</h3>
        <div class="chart-area">
            <Chart {init} options={price_chart_options} />
        </div>
    </div>
</main>

<style>
.dashboard-container {
  margin: 2rem 0rem;
  max-width: 100%;
  display: grid;
  gap: 0.5rem;
  font-family: sans-serif;
  grid-template-columns: repeat(8, minmax(0, 1fr));
}

.card {
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

#generation-pie {
  grid-column: 1 / 3;
}

#generation-chart {
  grid-column: 3 / 7;
}

#price-chart {
  grid-column: 1 / 3;
}

#interconnector-map {
  grid-column: 7 / -1;
}

.chart {
  min-width: 0;
  padding: 0.5rem;
  padding-top: 0;
}

.chart-area {
  height: 28rem;
  width: 100%;
  overflow: hidden;
}

@media (max-width: 1000px) {
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