using Core;
using Core.Repository;
using Core.Service;
using Infra.Repository;
using Microsoft.EntityFrameworkCore;
using Moq;

namespace Service.Tests
{
    [TestClass()]
    public class AutorServiceTests
    {
        private BibliotecaContext context;
        private IAutorService autorService;

        [TestInitialize]
        public void Initialize()
        {
            //Arrange
            var builder = new DbContextOptionsBuilder<BibliotecaContext>();
            builder.UseInMemoryDatabase("Biblioteca");
            var options = builder.Options;

            context = new BibliotecaContext(options);
            context.Database.EnsureDeleted();
            context.Database.EnsureCreated();
            var autores = new List<Autor>
                {
                    new() { Id = 1, Nome = "Machado de Assis", DataNascimento =  DateTime.Parse("1917-12-31")},
                    new() { Id = 2, Nome = "Ian S. Sommervile", DataNascimento = DateTime.Parse("1935-12-31")},
                    new() { Id = 3, Nome = "Gleford Myers", DataNascimento = DateTime.Parse("1900-11-20")},
                };

            context.AddRange(autores);
            context.SaveChanges();

            // Adaptador de persistência (AutorRepository) injetado no serviço via porta IAutorRepository
            var autorRepository = new AutorRepository(context);
            autorService = new AutorService(autorRepository);
        }

        [TestMethod()]
        public void CreateTest()
        {
            // Act
            autorService.Create(new Autor() { Id = 4, Nome = "Graciliano Ramos", DataNascimento = DateTime.Parse("1900-12-25") });
            // Assert
            Assert.AreEqual(4, autorService.GetAll().Count());
            var autor = autorService.Get(4);
            Assert.IsNotNull(autor);
            Assert.AreEqual("Graciliano Ramos", autor.Nome);
            Assert.AreEqual(DateTime.Parse("1900-12-25"), autor.DataNascimento);
        }

        [TestMethod()]
        public void DeleteTest()
        {
            // Act
            autorService.Delete(2);
            // Assert
            Assert.AreEqual(2, autorService.GetAll().Count());
            var autor = autorService.Get(2);
            Assert.AreEqual(null, autor);
        }

        [TestMethod()]
        public void EditTest()
        {
            //Act 
            var autor = autorService.Get(3);
            Assert.IsNotNull(autor);
            autor.Nome = "Paulo Coelho";
            autor.DataNascimento = DateTime.Parse("1950-11-21");
            autorService.Edit(autor);
            //Assert
            autor = autorService.Get(3);
            Assert.IsNotNull(autor);
            Assert.AreEqual("Paulo Coelho", autor.Nome);
            Assert.AreEqual(DateTime.Parse("1950-11-21"), autor.DataNascimento);
        }

        [TestMethod()]
        public void GetTest()
        {
            var autor = autorService.Get(1);
            Assert.IsNotNull(autor);
            Assert.AreEqual("Machado de Assis", autor.Nome);
            Assert.AreEqual(DateTime.Parse("1917-12-31"), autor.DataNascimento);
        }

        [TestMethod()]
        public void GetAllTest()
        {
            // Act
            var listaAutor = autorService.GetAll();
            // Assert
            Assert.IsInstanceOfType(listaAutor, typeof(IEnumerable<Autor>));
            Assert.IsNotNull(listaAutor);
            Assert.AreEqual(3, listaAutor.Count());
            Assert.AreEqual((uint)1, listaAutor.First().Id);
            Assert.AreEqual("Machado de Assis", listaAutor.First().Nome);
        }

        [TestMethod()]
        public void GetByNomeTest()
        {
            //Act
            var autores = autorService.GetByNome("Machado");
            //Assert
            Assert.IsNotNull(autores);
            Assert.AreEqual(1, autores.Count());
            Assert.AreEqual("Machado de Assis", autores.First().Nome);
        }

        #region Testes Unitários com Mock (Isolamento 100% da Regra de Negócio)

        [TestMethod()]
        [ExpectedException(typeof(ServiceException))]
        public void Create_AnoNascimentoMenorQue1000_LancaServiceExceptionSemChamarBanco()
        {
            // Arrange
            var mockRepo = new Mock<IAutorRepository>();
            var service = new AutorService(mockRepo.Object);
            var autorInvalido = new Autor { Id = 10, Nome = "Autor Antigo", DataNascimento = new DateTime(999, 1, 1) };

            // Act
            try
            {
                service.Create(autorInvalido);
            }
            finally
            {
                // Assert: garante que o repositório NUNCA foi chamado devido à regra de negócio
                mockRepo.Verify(r => r.Insert(It.IsAny<Autor>()), Times.Never);
            }
        }

        [TestMethod()]
        [ExpectedException(typeof(ServiceException))]
        public void Edit_AnoNascimentoMenorQue1000_LancaServiceExceptionSemChamarBanco()
        {
            // Arrange
            var mockRepo = new Mock<IAutorRepository>();
            var service = new AutorService(mockRepo.Object);
            var autorInvalido = new Autor { Id = 10, Nome = "Autor Antigo", DataNascimento = new DateTime(950, 5, 20) };

            // Act
            try
            {
                service.Edit(autorInvalido);
            }
            finally
            {
                // Assert: garante que o repositório NUNCA foi chamado devido à regra de negócio
                mockRepo.Verify(r => r.Update(It.IsAny<Autor>()), Times.Never);
            }
        }

        [TestMethod()]
        public void Create_AutorValido_ChamaRepositorioRetornaIdIsolado()
        {
            // Arrange: teste unitário puro, sem banco de dados, sem EF Core, sem DbContext
            var mockRepo = new Mock<IAutorRepository>();
            var autor = new Autor { Id = 5, Nome = "Clarice Lispector", DataNascimento = new DateTime(1920, 12, 10) };
            mockRepo.Setup(r => r.Insert(autor)).Returns(5);

            var service = new AutorService(mockRepo.Object);

            // Act
            var idCriado = service.Create(autor);

            // Assert
            Assert.AreEqual((uint)5, idCriado);
            mockRepo.Verify(r => r.Insert(autor), Times.Once);
        }

        #endregion
    }
}