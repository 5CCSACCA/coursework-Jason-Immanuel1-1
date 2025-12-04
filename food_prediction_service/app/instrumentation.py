from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

import os

from dotenv import load_dotenv

load_dotenv()

OTEL_ENDPOINT = os.getenv("OTEL_COLLECTOR_ENDPOINT", "http://otel-collector:4317")

def setup_otel(app) -> None:
    """Set up OpenTelemetry tracing and metrics for a FastAPI application.

    This function configures OTLP exporters for both traces and metrics,
    sets up resource attributes, and automatically instruments FastAPI routes
    and outgoing HTTP requests.

    Args:
        app: FastAPI application instance to instrument.

    Returns:
        None
    """

    # Define resource attributes for the food prediction service
    resource = Resource.create({
        "service.name": "food_prediction_service"
    })

    # Tracing setup
    tracer_provider = TracerProvider(resource=resource)
    # Use batch processing to export spans to OTLP collector
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint="http://otel-collector:4317",
                insecure=True  # Use insecure gRPC connection in production
            )
        )
    )
    trace.set_tracer_provider(tracer_provider)

    # Metrics setup
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint="http://otel-collector:4317",
            insecure=True  # Use insecure gRPC connection in production
        )
    )
    metrics.set_meter_provider(
        MeterProvider(resource=resource, metric_readers=[metric_reader])
    )

    # Auto-instrument FastAPI routes and outgoing HTTP requests
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
