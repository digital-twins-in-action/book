import logging
from opentelemetry import trace, metrics, _logs
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import ConsoleLogRecordExporter, BatchLogRecordProcessor

# 1. Tracing Setup (Prints Spans)
tp = TracerProvider()
tp.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tp)
tracer = trace.get_tracer(__name__)

# 2. Metrics Setup (Prints Aggregations)
reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
meter = metrics.get_meter(__name__)
drift_counter = meter.create_counter("drift_alerts")

# 3. Logs Setup (Prints Structured Logs)
lp = LoggerProvider()
lp.add_log_record_processor(BatchLogRecordProcessor(ConsoleLogRecordExporter()))
_logs.set_logger_provider(lp)
logger = logging.getLogger("DT_Ops")
logger.addHandler(LoggingHandler(logger_provider=lp))

# --- Execution ---
with tracer.start_as_current_span("sensor_sync"):
    drift = 2.5
    logger.warning("Drift detected!", extra={"value": drift})
    drift_counter.add(1, {"asset": "Pump-01"})
