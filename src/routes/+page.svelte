<script>
    import { Chart } from 'svelte-echarts';
    import { onMount } from 'svelte';
    import { init, use, registerMap } from 'echarts/core';
    import { LineChart,LinesChart, PieChart, MapChart } from 'echarts/charts';
    import { GraphicComponent, ToolboxComponent, DataZoomComponent, GridComponent, GeoComponent, VisualMapComponent, TooltipComponent, LegendComponent } from 'echarts/components';
    import { CanvasRenderer } from 'echarts/renderers';
    import europeGeoJSON from '$lib/assets/europe.geojson?raw';
    import Price from './Price.svelte'
    import CarbonIntensity from './CarbonIntensity.svelte'
    import Interconnectors from './Interconnectors.svelte'
    
    // now with tree-shaking
    use([LineChart, LinesChart, PieChart, MapChart, ToolboxComponent, DataZoomComponent, GraphicComponent, GridComponent, CanvasRenderer, GeoComponent, VisualMapComponent, TooltipComponent, LegendComponent])

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

    function sumMultipleArrays(firstArray, ...otherArrays) {
        return firstArray.map(([key, value], index) => {
            const total = otherArrays.reduce((sum, currentArray) => {
                return sum + currentArray[index][1];
            }, value);
            return [key, total];
        })
    }

    function coordsOrder(ukCoord, otherCoord, value) {
        return value > 0 ? [otherCoord, ukCoord] : [ukCoord, otherCoord];        
    }

    const filterByCategory = (cat, conv=1) => data?.metrics?.filter(a => a.category === cat).map(a => [utcToUK(a.timestamp), a.value / conv]);

    const europeJSON = JSON.parse(europeGeoJSON);
    registerMap('europe', europeJSON);

    // PRICE DATA
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

    // INTERCONNECTOR DATA
    let IEgreenlink = filterByCategory("INTGRNL", MW_TO_GW);
    let IEeastwest = filterByCategory("INTEW", MW_TO_GW);
    let IEmoyle = filterByCategory("INTIRL", MW_TO_GW);
    let IEinter = sumMultipleArrays(IEgreenlink, IEeastwest, IEmoyle)
    let IEnow = IEinter[IEinter.length - 1][1];
    let FRIFA = filterByCategory("INTFR", MW_TO_GW)
    let FRIFAtwo = filterByCategory("INTIFA2", MW_TO_GW)
    let FReleclink = filterByCategory("INTELEC", MW_TO_GW)
    let FRinter = sumMultipleArrays(FRIFA, FRIFAtwo, FReleclink)
    let FRnow = FRinter[FRinter.length - 1][1];
    let NOnsl = filterByCategory("INTNSL", MW_TO_GW)
    let NOinter = NOnsl
    let NOnow = NOinter[NOinter.length - 1][1];
    let DNviking = filterByCategory("INTVKL", MW_TO_GW)
    let DNinter = DNviking
    let DNnow = DNinter[DNinter.length - 1][1];
    let NLbritned = filterByCategory("INTNED", MW_TO_GW)
    let NLinter = NLbritned
    let NLnow = NLinter[NLinter.length - 1][1];
    let BEnemo = filterByCategory("INTNEM", MW_TO_GW);
    let BEinter = BEnemo
    let BEnow = BEinter[BEinter.length - 1][1];
    let total_importexport = sumMultipleArrays(IEinter, FRinter, NOinter, DNinter, NLinter, BEinter);
    let total_importexportNow = total_importexport[total_importexport.length - 1][1];
    const dashArray = [10, 1];

    // GENERATION DATA
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

    // CARBON INTENSITY
    let carbon_intensity_data = filterByCategory('carbon_intensity');

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

    const raw_gen_data = [
        {
            name: "Other",
            data: other_data,
        },
        {
            name: "Coal",
            data: coal_data,
        },
        {
            name: "Oil",
            data: oil_data,
        },
        {
            name: "Biomass",
            data: biomass_data,
        },
        {
            name: "Nuclear",
            data: nuclear_data,
        },
        {
            name: "Gas",
            data: gas_data,
        },
        {
            name: "Hydro",
            data: hydro_data,
        },
        {
            name: "Solar",
            data: solar_data,
        },
        {
            name: "Wind",
            data: total_wind_data,
        }
    ]
    const masterTimeline = [...new Set(raw_gen_data.flatMap(s => s.data.map(d => d[0])))].sort();
    const gen_data_series_processed = raw_gen_data.map(series => {
        const dataMap = new Map(series.data);
        return {
            ...series,
            data: masterTimeline.map(t => [t, dataMap.get(t) ?? 0]),
            type: 'line',
            symbol: 'none',
            smooth: true,
            stack: 'Total',
            connectNulls: true,
            areaStyle: {}
        };
    });
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
        series: gen_data_series_processed.filter(series => series.data.some(item => item[1] !== 0))
    };  

    const raw_pie_data = [
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
    const raw_type_data = [
        { value: coal_data[coal_data.length - 1][1] + oil_data[oil_data.length - 1][1] + gas_data[gas_data.length - 1][1], name: 'Fossil fuels', itemStyle: {color: '#ff4848'}},
        { value: solar_data[solar_data.length - 1][1] + hydro_data[hydro_data.length - 1][1] + total_wind_data[total_wind_data.length - 1][1], name: 'Renewable', itemStyle: {color: '#74ff8b'}},
        { value: other_data[other_data.length - 1][1] + biomass_data[biomass_data.length - 1][1] + nuclear_data[nuclear_data.length - 1][1], name: 'Other', itemStyle: {color: '#c44dff'}}
    ]
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
                name: 'Individual Generation',
                type: 'pie',
                radius: ['45%', '80%'],
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
                data: raw_pie_data.filter(item => item.value !== 0)
            },
            {
                name: 'Renewable vs non-renewable',
                type: 'pie',
                radius: ['34%', '44%'],
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
                data: raw_type_data.filter(item => item.value !== 0)
            }
        ]
    }

    let inter_map_options = $state({
    geo: {
        map: 'europe',
        roam: true,
        itemStyle: {
            borderColor: '#403288',
            borderWidth: 1.0
        },
        boundingCoords: [
            [0.4, 44],
            [0.5, 61]
        ],
        layoutCenter: ['55%','55%'],
        aspectScale: 0.9,        // < 1 compresses vertically, > 1 horizontally
        nameProperty: 'NAME',
        label: { show: false },
        emphasis: { disabled: true, label: { show: false } },
        select: { disabled: true}
    },
    tooltip: {
        trigger: 'item',
        formatter: function (params) {
            console.log(params)
            if (params.seriesType === 'lines') {
                return `<b>${params.data.name}:</b> ${params.value.toFixed(2)} GW<br/>Capacity: ${params.data.capacity} GW`;
            }
            if (params.value === undefined || isNaN(params.value)) {
                return '';
            }
                return `<b>${params.name}</b><br/> ${(params.value).toFixed(2)} GW`;
        }
    },
    visualMap: [
        {
        orient: 'horizontal',
        left: 0,
        seriesIndex: 0,
        bottom: 0,
        show: false,
        min: -Math.max(FRnow, IEnow, NLnow, NOnow, DNnow, BEnow),
        max: Math.max(FRnow, IEnow, NLnow, NOnow, DNnow, BEnow),
        inRange: { color: ['#ff0000','#FFFFFF', '#77ff00'] }
        }
    ],
    series: [
        {
            type: 'map',
            geoIndex: 0,
            name: 'Transfer',
            data: [
                { name: 'France', value: FRnow },
                { name: 'Ireland', value: IEnow },
                { name: 'Netherlands', value: NLnow },
                { name: 'Norway', value: NOnow },
                { name: 'Denmark', value: DNnow },
                { name: 'Belgium', value: BEnow }
            ],
            select: {
                disabled: true
            }
        },
        {
            type: 'lines',
            coordinateSystem: 'geo',
            silent: false,
            data: [
                {
                    name: 'East-West',
                    capacity: 0.5,
                    value: IEeastwest[IEeastwest.length - 1][1],
                    coords: coordsOrder([-3.072778, 53.227222],[-6.5675, 53.471111], IEeastwest[IEeastwest.length - 1][1])
                },
                {
                    name: 'Greenlink',
                    capacity: 0.5,
                    value: IEgreenlink[IEgreenlink.length - 1][1],
                    coords: coordsOrder([-4.988, 51.683], [-6.991, 52.281], IEgreenlink[IEgreenlink.length - 1][1])
                },
                {
                    name: 'Moyle',
                    capacity: 0.5,
                    value: IEmoyle[IEmoyle.length - 1][1],
                    coords: coordsOrder([-4.980556, 55.069444],[-5.769722, 54.842778], IEmoyle[IEmoyle.length - 1][1])
                },
                {
                    name: 'IFA',
                    capacity: 2.0,
                    value: FRIFA[FRIFA.length - 1][1],
                    coords: coordsOrder([0.947222, 50.915],[1.784722, 50.903056], FRIFA[FRIFA.length - 1][1])
                },
                {
                    name: 'IFA2',
                    capacity: 1.0,
                    value: FRIFAtwo[FRIFAtwo.length - 1][1],
                    coords: coordsOrder([-1.194,50.818],[-0.262,49.1108], FRIFAtwo[FRIFAtwo.length - 1][1])
                },
                {
                    name: 'Eleclink',
                    capacity: 1.0,
                    value: FReleclink[FReleclink.length - 1][1],
                    coords: coordsOrder([1.1447,51.0984],[1.7806,50.9202], FReleclink[FReleclink.length - 1][1])
                },
                {
                    name: 'North Sea Link',
                    capacity: 1.4,
                    value: NOnsl[NOnsl.length - 1][1],
                    coords: coordsOrder([-1.5183,55.1439],[6.6722,59.4844], NOnsl[NOnsl.length - 1][1])
                },
                {
                    name: 'Viking Link',
                    capacity: 1.4,
                    value: DNviking[DNviking.length - 1][1],
                    coords: coordsOrder([-0.220556,52.930278],[8.709722,55.523056], DNviking[DNviking.length - 1][1])
                },
                {
                    name: 'Britned',
                    capacity: 1.0,
                    value: NLbritned[NLbritned.length - 1][1],
                    coords: coordsOrder([0.716667,51.44],[4.021389,51.9575], NLbritned[NLbritned.length - 1][1])
                },
                {
                    name: 'Nemo',
                    capacity: 1.0,
                    value: BEnemo[BEnemo.length - 1][1],
                    coords: coordsOrder([1.3464,51.3072],[3.21,51.265], BEnemo[BEnemo.length - 1][1])
                }
            ],
            lineStyle: {
                color: 'black',
                type: [5, 5],
                width: 3,
                curveness: 0
            },
            effect: {
                show: true,
                period: 4,
                trailLength: 0.1,
                symbol: 'arrow',
                symbolSize: 6,
                loop: true
            }
        }
    ]
    });

    let inter_data_options = {
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
            data: ["Ireland", "France", "Norway", "Denmark", "Netherlands", "Belgium"],
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
                name: "Ireland",
                data: IEinter,
                type: "line",
                symbol: 'none',
                smooth: true,
            },
            {
                name: "France",
                data: FRinter,
                type: "line",
                symbol: 'none',
                smooth: true,
            },
            {
                name: "Norway",
                data: NOinter,
                type: "line",
                symbol: 'none',
                smooth: true,
            },
            {
                name: "Denmark",
                data: DNinter,
                type: "line",
                symbol: 'none',
                smooth: true,
            },
            {
                name: "Netherlands",
                data: NLinter,
                type: "line",
                symbol: 'none',
                smooth: true,
            },
            {
                name: "Belgium",
                data: BEinter,
                type: "line",
                symbol: 'none',
                smooth: true,
            }
        ]
    }; 

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

    let tabs = [
        {name: "Price", comp: Price, options: price_chart_options},
        {name: "Carbon Intensity", comp: CarbonIntensity, options: carbon_intensity_options},
        {name: "Interconnectors", comp: Interconnectors, options: inter_data_options}
    ];
    let cur = $state(tabs[0]);
    let DynamicComponent = $derived(cur.comp);
    let currentOptions = $derived(cur.options)
</script>

<div class="content">
    <main class="dashboard-container">
        <div class="card info" id="time">
            <h3>{now.toLocaleString('en-GB',{timeZone:'Europe/London', }).substring(0,17)}</h3>
        </div>
        <div class="card info" id="generation">
            <p><strong>Generation:</strong> {total_generation_data.toFixed(2)} GW + <strong>Imports/Exports:</strong> {(total_importexportNow).toFixed(2)} GW = {(total_generation_data + total_importexportNow).toFixed(2)} GW</p>
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
    </main>
    <div class="tab-section">
        <div class="tabs">
            {#each tabs as tab}
                <button class:selected={cur.name === tab.name} onclick={() => (cur=tab)}>
                    <strong>{tab.name}</strong>
                </button>
            {/each}
        </div>
        <div class="tab-content">
            <div id="tab-chart">
                <DynamicComponent options={currentOptions} />
            </div>
        </div>
    </div>
</div>

<style>

.content {
    margin: 1.5rem auto;
    max-width: 1600px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    font-family: sans-serif;
}

.tab-section {
    display: flex;
    flex-direction: column;
    .tab-content {
        border: 1px solid #abc;
        border-radius: 0 10px 10px 10px;
        background-color: #fff;
        padding: 1em;
        display: grid;
        grid-template-columns: repeat(2, minmax(0,800px))
    }
}

.tabs {
    display: flex;
}

button {
    cursor: pointer;
    padding: 0.5rem 1rem;
    border: 1px solid transparent;
    margin-bottom: -1px;
    background-color: #fff;
    border-bottom-color: #abc;
    font-size: 1rem;
}

button.selected {
    border-top-right-radius: 8px;
    border-top-left-radius: 8px;
    border-top-width: 8px;
    border-color: #abc #abc #fff;
}

.dashboard-container {
  display: grid;
  gap: 0.5rem;
  grid-template-columns: repeat(8, minmax(0, 200px));
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
  grid-column: 4 / 6;
  
}

#interconnector-data-chart {
  grid-column: 6 / -1;
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

  #carbon-intensity-chart {
    grid-column: 1 / 5;
  }

  #interconnector-data-chart {
    grid-column: 5 / -1;
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

    #carbon-intensity-chart {
        grid-column: 1 / -1;
    }

    #interconnector-data-chart {
        grid-column: 1 / -1;
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

    #tab-chart {
        grid-column: 1 / -1;
    }
}

</style>