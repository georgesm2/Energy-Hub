<script>
    import { Chart } from 'svelte-echarts';
    import { onMount } from 'svelte';
    import { init, use, registerMap } from 'echarts/core';
    import { LineChart, PieChart, MapChart } from 'echarts/charts';
    import { GraphicComponent, ToolboxComponent, DataZoomComponent, GridComponent, GeoComponent, VisualMapComponent, TooltipComponent, LegendComponent } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';
    import europeGeoJSON from '$lib/assets/europe.geojson?raw';
    
    // now with tree-shaking
    use([LineChart, PieChart,MapChart, ToolboxComponent, DataZoomComponent, GraphicComponent, GridComponent, CanvasRenderer, GeoComponent, VisualMapComponent, TooltipComponent, LegendComponent])

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
    // make sure that the two arrays are the same length as octopus agile is often available earlier than market price
    if (market_price_data.length > agile_price_data.length) {
        agile_price_data.push([market_price_data[market_price_data.length - 1][0], agile_price_data[agile_price_data.length - 1][1]]);
    } else if (agile_price_data.length > market_price_data.length) {
        market_price_data.push([agile_price_data[agile_price_data.length - 1][0], market_price_data[market_price_data.length - 1][1]]);
    }
    let price_cap_data = filterByCategory('price_cap');
    price_cap_data.push([market_price_data[market_price_data.length - 1][0], price_cap_data[price_cap_data.length - 1][1]]);
    // change price cap data to only include the period being plotted
    const start_timestamp = market_price_data[0][0];
    const past_price_cap_data = price_cap_data.filter(a => a[0] < start_timestamp);
    const current_price_cap_data = price_cap_data.filter(a => a[0] >= start_timestamp);
    const baseline_cap = past_price_cap_data[past_price_cap_data.length - 1];
    baseline_cap[0] = start_timestamp;
    price_cap_data = [baseline_cap, ...current_price_cap_data];
    let price_chart_options = {
        tooltip: {
            trigger: "axis",
            formatter: function (params) {
                let text = params[0].axisValueLabel + "<br>";
                let currentTime = new Date(params[0].value[0]);
                params.forEach(p => {
                    if (p.seriesName === "Ofgem Price Cap") {
                        return;
                    }
                    text += `${p.marker} ${p.seriesName}: ${p.value[1].toFixed(3)} £/kWh<br>`;
                });
                text += `${`<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:#FFDB5C;"></span>`} Price Cap: ${price_cap_data.filter(a => new Date(a[0]) <= currentTime).pop()[1].toFixed(3)} £/kWh`;
                return text;
            }
        },
        toolbox: {
            feature: {
            restore: {},
            saveAsImage: {}
            }
        },
        dataZoom: [
            {
                type: 'inside',
                filterMode: 'none',
                start: 90,
                end: 100
            },
            {
                start: 90,
                end: 100
            }
        ],
        legend: {
            data: ["Wholesale Market", "Octopus Agile", "Ofgem Price Cap"],
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
            },
            {
                name: "Ofgem Price Cap",
                data: price_cap_data,
                type: "line",
                step: 'end',
            }
        ]
    };

    let biomass_data = filterByCategory('BIOMASS', MW_TO_GW);
    let ccgt_data = filterByCategory('CCGT', MW_TO_GW);
    let ocgt_data = filterByCategory('OCGT', MW_TO_GW);
    let gas_data = Object.entries([...ccgt_data,...ocgt_data].reduce((a, [timestamp, value]) => {
        a[timestamp] = (a[timestamp] || 0) + value;
        return a;}, {})
        ).map(([timestamp, value]) => [timestamp, value]);
    let coal_data = filterByCategory('COAL', MW_TO_GW);
    let oil_data = filterByCategory('OIL', MW_TO_GW);
    let hydro_data = filterByCategory('NPSHYD', MW_TO_GW);
    let nuclear_data = filterByCategory('NUCLEAR', MW_TO_GW);
    let solar_data = filterByCategory('SOLAR', MW_TO_GW);
    let total_wind_data = filterByCategory('WIND', MW_TO_GW);
    let other_data = filterByCategory('OTHER', MW_TO_GW);
    let total_generation_data = biomass_data[biomass_data.length-1][1] + gas_data[gas_data.length-1][1] + coal_data[coal_data.length-1][1] + 
    oil_data[oil_data.length-1][1] + hydro_data[hydro_data.length-1][1] + nuclear_data[nuclear_data.length-1][1] + solar_data[solar_data.length-1][1] + 
    total_wind_data[total_wind_data.length-1][1] + other_data[other_data.length-1][1];
    let gen_chart_options = {
        tooltip: {
            trigger: "axis",
            formatter: function (params) {
                let text = params[0].axisValueLabel + "<br>";
                params.forEach(p => {
                    if (p.value[1] === 0) {
                        return;
                    }
                    text += `${p.marker} ${p.seriesName}: ${p.value[1].toFixed(2)} GW<br>`;
                });
                return text;
            }
        },
        toolbox: {
            feature: {
            restore: {},
            saveAsImage: {}
            }
        },
        dataZoom: [
            {
                type: 'inside',
                start: 90,
                zoomLock: true, 
                end: 100
            },
            {
                start: 90,
                end: 100
            }
        ],
        legend: {
            data: ["Biomass", "Coal", "Gas", "Hydro",  "Nuclear", "Oil", "Solar", "Wind", "Other"],
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
                name: "Other",
                data: other_data,
                type: "line",
                symbol: 'none',
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Coal",
                data: coal_data,
                type: "line",
                symbol: 'none',
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Oil",
                data: oil_data,
                type: "line",
                symbol: 'none',
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Biomass",
                data: biomass_data,
                type: "line",
                symbol: 'none',
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Nuclear",
                data: nuclear_data,
                type: "line",
                symbol: 'none',
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Gas",
                data: gas_data,
                type: "line",
                symbol: 'none',
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Hydro",
                data: hydro_data,
                type: "line",
                symbol: 'none',
                smooth: true,
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Solar",
                data: solar_data,
                type: "line",
                smooth: true,
                symbol: 'none',
                stack: 'Total',
                areaStyle: {}
            },
            {
                name: "Wind",
                data: total_wind_data,
                type: "line",
                symbol: 'none',
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
                return params.name + ': ' + params.value.toFixed(2).toString() + ' GW (' + params.percent.toFixed(1) + '%)';
            }
        },
        legend: {
            data: ["Biomass", "Coal", "Gas", "Hydro",  "Nuclear", "Oil", "Solar", "Wind", "Other"],
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
                    { value: other_data[other_data.length - 1][1], name: 'Other' },
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
    let IEgreenlink = filterByCategory("INTGRNL");
    let IEeastwest = filterByCategory("INTEW");
    let IEmoyle = filterByCategory("INTIRL");
    let IEinter = IEgreenlink[IEgreenlink.length - 1][1] + IEeastwest[IEeastwest.length - 1][1] + IEmoyle[IEmoyle.length - 1][1];
    let FRIFA = filterByCategory("INTFR")
    let FRIFAtwo = filterByCategory("INTIFA2")
    let FReleclink = filterByCategory("INTELEC")
    let FRinter = FRIFA[FRIFA.length - 1][1] + FRIFAtwo[FRIFAtwo.length - 1][1] + FReleclink[FReleclink.length - 1][1];
    let NOnsl = filterByCategory("INTNSL")
    let NOinter = NOnsl[NOnsl.length - 1][1];
    let DNviking = filterByCategory("INTVKL")
    let DNinter = DNviking[DNviking.length - 1][1];
    let NLbritned = filterByCategory("INTNED")
    let NLinter = NLbritned[NLbritned.length - 1][1];
    let BEnemo = filterByCategory("INTNEM");
    let BEinter = BEnemo[BEnemo.length - 1][1];
    let total_importexport = IEinter + FRinter + NOinter + DNinter + NLinter + BEinter;

    let inter_map_options = {
    geo: {
        map: 'europe',
        roam: false,
        itemStyle: {
            borderColor: '#403288',
            borderWidth: 1.0
        },
        boundingCoords: [
            [0.4, 40],
            [0.5, 64]
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
            if (params.value === undefined || isNaN(params.value)) {
                return '';
            }
                return params.name + ': ' + (params.value / 1000).toFixed(2).toString() + ' GW';
            }
    },
    visualMap: [
        {
        orient: 'horizontal',
        left: 0,
        bottom: 0,
        show: false,
        min: -Math.max(FRinter, IEinter, NLinter, NOinter, DNinter, BEinter),
        max: Math.max(FRinter, IEinter, NLinter, NOinter, DNinter, BEinter),
        inRange: { color: ['#ff0000','#FFFFFF', '#77ff00'] }
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

    let carbon_intensity_data = filterByCategory('carbon_intensity');
    let carbon_intensity_options = {
        tooltip: {
            trigger: "axis",
            formatter: function (params) {
                let text = params[0].axisValueLabel + "<br>";
                params.forEach(p => {
                    text += `${p.marker} ${p.seriesName}: ${p.value[1].toFixed(2)} gCO2/kWh<br>`;
                });
                return text;
            }
        },
        toolbox: {
            feature: {
            restore: {},
            saveAsImage: {}
            }
        },
        dataZoom: [
            {
                type: 'inside',
                filterMode: 'none',
                start: 90,
                end: 100
            },
            {
                start: 90,
                end: 100
            }
        ],
        legend: {
            data: ["Carbon Intensity"],
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
                name: "Carbon Intensity",
                data: carbon_intensity_data,
                type: "line",
                smooth: true,
            }
        ]
    };


</script>

<main class="dashboard-container">
    <div class="card info" id="time">
        <p>{now.toLocaleString('en-GB',{timeZone:'Europe/London', }).substring(0,17)}</p>
    </div>
    <div class="card info" id="generation">
        <p>Generation: {total_generation_data.toFixed(2)} GW + Imports/Exports: {(total_importexport/1000).toFixed(2)} GW = {(total_generation_data + total_importexport/1000).toFixed(2)} GW</p>
    </div>
    <div class="card chart" id="generation-pie">
        <h3>Generation Breakdown</h3>
        <div class="chart-area">
            <Chart {init} options={gen_pie_options} />
        </div>
    </div>
    <div class="card chart" id="generation-chart">
        <h3>Generation by Type / GW</h3>
        <div class="chart-area">
            <Chart {init} options={gen_chart_options} />
        </div>
    </div>
    <div class="card chart" id="interconnector-map">
        <h3>Imports / Exports</h3>
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
    <div class="card chart" id="carbon-intensity-chart">
        <h3>Carbon Intensity gCO2 / kWh</h3>
        <div class="chart-area">
            <Chart {init} options={carbon_intensity_options} />
        </div>
    </div>
</main>

<style>
.dashboard-container {
  margin: 1.5rem auto;
  max-width: 1600px;
  align-items: center;
  display: grid;
  gap: 0.5rem;
  font-family: sans-serif;
  grid-template-columns: repeat(8, minmax(0, 200px));
}

.card {
  background-color: #fff;
  border-radius: 10px;
  min-width: 0;
  box-sizing: border-box;
  text-align: center;
}

.info {
    display: flex;
    justify-content: center;
    align-items: center;
}

#time {
  grid-column: 1 / 3;
}

#generation {
    grid-column: 3 / -1;
}

#generation-pie {
  grid-column: 1 / 3;
}

#generation-chart {
  grid-column: 3 / 7;
}

#price-chart {
  grid-column: 1 / 4;
}

#interconnector-map {
  grid-column: 7 / -1;
}

#carbon-intensity-chart {
  grid-column: 4 / 7;
}


.chart {
  min-width: 0;
  box-sizing: border-box;
  padding: 0rem;
  padding-top: 0;
}

.chart-area {
  height: 26rem;
  width: 100%;
  overflow: hidden;
}

@media (max-width: 1300px) {
  #interconnector-map {
    grid-column: 1 / 4;
  }

  #generation-chart {
    grid-column: 4 / -1;
  }

  #generation-pie {
    grid-column: 1 / 4;
  }

  #price-chart {
    grid-column: 4 / -1;
  }
  
}

@media (max-width: 850px) {
    #time {
        grid-column: 1 / -1;
    }
    #generation {
        grid-column: 1 / -1;
    }
    #interconnector-map {
      grid-column: 1 / 5;
    }
  
    #generation-chart {
      grid-column: 1 / -1;
    }
  
    #generation-pie {
      grid-column: 1 / -1;
    }
  
    #price-chart {
      grid-column: 5 / -1;
    }
  
}

@media (max-width: 610px) {
    #interconnector-map {
      grid-column: 1 / -1;
    }
  
    #generation-chart {
      grid-column: 1 / -1;
    }
  
    #generation-pie {
      grid-column: 1 / -1;
    }
  
    #price-chart {
      grid-column: 1 / -1;
    }

    .chart-area {
        height: 25rem;
    }
  
}

</style>