const now = new Date()

const getLondonISOString = (dateObj) => {
    const formatter = new Intl.DateTimeFormat('sv-SE', {
        timeZone: 'Europe/London',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    });

    const formatted = formatter.format(dateObj);

    return formatted.replace(' ', 'T');
}

const todayURI = encodeURIComponent(getLondonISOString(now));
const past = new Date(now.getTime() - 24*60*60*1000);
const pastURI = encodeURIComponent(getLondonISOString(past));

export const load = async({ url, fetch }) => {
    const priceRes = await fetch(`https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index?from=${pastURI}Z&to=${todayURI}Z&dataProviders=APXMIDP`)
    const priceData = await priceRes.json()
    const price = priceData.data

    const genRes = await fetch(`https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type?from=${pastURI}Z&to=${todayURI}Z`)
    const genData = await genRes.json()
    const generation = genData.data

    const demRes = await fetch(`https://data.elexon.co.uk/bmrs/api/v1/demand/actual/total?from=${todayURI.substring(0,10)}&to=${todayURI}`)
    const demData = await demRes.json()
    const demand = demData.data

    const agileRes = await fetch(`https://api.octopus.energy/v1/products/AGILE-24-10-01/electricity-tariffs/E-1R-AGILE-24-10-01-A/standard-unit-rates/?period_from=${pastURI}Z&period_to=${todayURI}Z`)
    const agileData = await agileRes.json()
    while (agileData.next !== null) {
        const agileResNext = await fetch(agileData.next)
        const agileDataNext = await agileResNext.json()
        agileData.results = agileData.results.concat(agileDataNext.results)
        agileData.next = agileDataNext.next
    }
    const agile = agileData.results

    return {
        price,
        generation,
        demand,
        agile,
        now: now.toTimeString().substring(0,5)
    }
}