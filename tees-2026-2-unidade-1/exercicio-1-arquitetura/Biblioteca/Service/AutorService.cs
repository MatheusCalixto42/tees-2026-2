using Core;
using Core.Datatables;
using Core.DTO;
using Core.Repository;
using Core.Service;

namespace Service
{
    /// <summary>
    /// Implementa serviços e regras de negócio para manter dados do autor.
    /// Desacoplado do mecanismo de banco de dados via IAutorRepository.
    /// </summary>
    public class AutorService : IAutorService
    {
        private readonly IAutorRepository autorRepository;

        public AutorService(IAutorRepository autorRepository)
        {
            this.autorRepository = autorRepository;
        }

        public uint Create(Autor autor)
        {
            if (autor.DataNascimento.Year < 1000)
                throw new ServiceException("O ano de nascimento de autor deve ser maior do que 1000. Favor informar nova data.");

            return autorRepository.Insert(autor);
        }

        public void Delete(uint id)
        {
            autorRepository.Delete(id);
        }

        public void Edit(Autor autor)
        {
            if (autor.DataNascimento.Year < 1000)
                throw new ServiceException("O ano de nascimento de autor deve ser maior do que 1000. Favor informar nova data.");

            autorRepository.Update(autor);
        }

        public Autor? Get(uint id)
        {
            return autorRepository.Get(id);
        }

        public IEnumerable<Autor> GetAll()
        {
            return autorRepository.GetAll();
        }

        public IEnumerable<Autor> GetAllOrderByNome()
        {
            return autorRepository.GetAllOrderByNome();
        }

        public int GetCountAutores()
        {
            return autorRepository.GetCountAutores();
        }

        public IEnumerable<Autor> GetByName(string nomeAutor)
        {   
            return autorRepository.GetByName(nomeAutor);
        }

        public IEnumerable<Autor> GetOrderByDescending()
        {
            return autorRepository.GetOrderByDescending();
        }

        public IEnumerable<AutorDto> GetByNome(string nome)
        {
            return autorRepository.GetByNome(nome);
        }

        public DatatableResponse<Autor> GetDataPage(DatatableRequest request)
        {
            return autorRepository.GetDataPage(request);
        }
    }
}
