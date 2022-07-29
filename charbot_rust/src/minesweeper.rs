mod field;
pub mod game;
mod common;
use pyo3::prelude::*;

const DOCSTRING: &str = "Rust based reimplementation of minesweeper";

pub(crate) fn register_minesweeper(py: Python, m: &PyModule) -> PyResult<()> {
    let minesweeper = PyModule::new(py, "minesweeper")?;
    minesweeper.add_class::<game::Game>()?;
    minesweeper.add_class::<game::ChordResult>()?;
    minesweeper.add_class::<game::RevealResult>()?;
    minesweeper.add("__doc__", DOCSTRING)?;
    m.add_submodule(minesweeper)?;
    Ok(())
}
