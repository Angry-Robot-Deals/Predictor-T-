use pyo3::prelude::*;
use ccxt::exchange::{Exchange, Value, normalize, ValueTrait};
use ccxt::binance::{Binance, BinanceImpl};

use serde_json::json;
const UNDEFINED: Value = Value::Undefined;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}


#[pyfunction]
fn call_rust_sleep(py: Python) -> PyResult<String> {
    Ok("call_rust_sleep".to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn integration(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
