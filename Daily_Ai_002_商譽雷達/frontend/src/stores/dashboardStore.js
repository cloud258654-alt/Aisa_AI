var DashboardStore = (function () {
  var state = {
    brandScore: 92.4,
    storeHealth: 98.1,
    csat: 4.82,
    resolutionRate: 94.5,
    riskScore: 12,
    streamItems: [],
    journeyData: null,
    selectedStore: 'all',
    isLoading: false,
    isStreamRunning: true,
    connectionStatus: 'connected',
    sandboxResults: null,
    storeRankings: [],
    predictions: [],
    learningCases: null
  };

  var listeners = [];

  function getState() {
    return state;
  }

  function setState(partial) {
    var prevState = {};
    for (var key in state) { prevState[key] = state[key]; }
    for (var k in partial) { state[k] = partial[k]; }
    for (var i = 0; i < listeners.length; i++) {
      listeners[i](state, prevState);
    }
  }

  function subscribe(fn) {
    listeners.push(fn);
    return function () {
      var idx = listeners.indexOf(fn);
      if (idx > -1) { listeners.splice(idx, 1); }
    };
  }

  function updateMetrics(brand, store, csat, res, risk) {
    setState({
      brandScore: brand,
      storeHealth: store,
      csat: csat,
      resolutionRate: res,
      riskScore: risk
    });
  }

  function addStreamItem(item) {
    var items = [item].concat(state.streamItems);
    if (items.length > 50) { items = items.slice(0, 50); }
    setState({ streamItems: items });
  }

  function setStreamItems(items) {
    setState({ streamItems: items });
  }

  function clearStream() {
    setState({ streamItems: [] });
  }

  function setJourneyData(data) {
    setState({ journeyData: data });
  }

  function setSelectedStore(store) {
    setState({ selectedStore: store });
  }

  function setLoading(loading) {
    setState({ isLoading: loading });
  }

  function setConnectionStatus(status) {
    setState({ connectionStatus: status });
  }

  function setStreamRunning(running) {
    setState({ isStreamRunning: running });
  }

  function setSandboxResults(results) {
    setState({ sandboxResults: results });
  }

  return {
    getState: getState,
    setState: setState,
    subscribe: subscribe,
    updateMetrics: updateMetrics,
    addStreamItem: addStreamItem,
    setStreamItems: setStreamItems,
    clearStream: clearStream,
    setJourneyData: setJourneyData,
    setSelectedStore: setSelectedStore,
    setLoading: setLoading,
    setConnectionStatus: setConnectionStatus,
    setStreamRunning: setStreamRunning,
    setSandboxResults: setSandboxResults
  };
})();
