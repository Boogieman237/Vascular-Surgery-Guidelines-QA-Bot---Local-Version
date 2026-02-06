# Contributing to Medical Guidelines QA Bot

Thank you for your interest in contributing! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/medical-guidelines-qabot/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check [existing feature requests](https://github.com/yourusername/medical-guidelines-qabot/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
2. Create a new issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Why it would be useful
   - Any alternatives you've considered

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/medical-guidelines-qabot.git
   cd medical-guidelines-qabot
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clear, commented code
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   python3 instant_test.py
   pytest tests/
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## 📝 Code Style

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic
- Keep functions focused and small

### Example:
```python
def calculate_similarity(query: str, documents: list) -> list:
    """
    Calculate similarity scores between query and documents.
    
    Args:
        query: User's search query
        documents: List of document chunks
        
    Returns:
        List of (document, score) tuples sorted by relevance
    """
    # Implementation here
    pass
```

## 🧪 Testing

### Run Tests
```bash
# Quick test
python3 instant_test.py

# Full test suite
pytest tests/

# With coverage
pytest --cov=. tests/
```

### Writing Tests
Add tests to `tests/` directory:
```python
def test_pdf_loading():
    """Test that PDFs load correctly"""
    loader = PyMuPDFLoader("test.pdf")
    docs = loader.load()
    assert len(docs) > 0
```

## 📚 Documentation

- Update README.md if adding features
- Add docstrings to new functions
- Update QUICKSTART.md if changing setup
- Add examples for new functionality

## 🏷️ Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested

## 🎯 Development Priorities

### High Priority
- Bug fixes
- Performance improvements
- Security updates
- Documentation improvements

### Medium Priority
- New features with clear use cases
- UI/UX improvements
- Additional LLM support
- Better error handling

### Lower Priority
- Nice-to-have features
- Code refactoring
- Style improvements

## 🔍 Code Review Process

1. Maintainer reviews your PR
2. Feedback or approval given
3. Make requested changes if needed
4. Once approved, PR is merged

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Given GitHub contributor badge

## 💬 Communication

- **Issues**: For bugs and features
- **Discussions**: For questions and ideas
- **Pull Requests**: For code contributions

## 🚀 Getting Started Checklist

- [ ] Fork the repository
- [ ] Set up development environment
- [ ] Read the codebase
- [ ] Find an issue to work on
- [ ] Ask questions if needed
- [ ] Make your contribution
- [ ] Submit pull request

## 📖 Resources

- [Python Style Guide](https://pep8.org/)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)
- [LangChain Documentation](https://python.langchain.com/)

## 🎓 Learning Resources

New to contributing? Start here:
- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [First Contributions](https://github.com/firstcontributions/first-contributions)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

**Thank you for contributing to making medical information more accessible!** 🏥
