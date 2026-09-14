using Core;
using Core.Datatables;
using Core.DTO;
using Core.Repository;
using Microsoft.EntityFrameworkCore;

namespace Infra.Repository
{
    /// <summary>
    /// Adaptador de persistência (Driven/Output Adapter) para o agregado Autor usando Entity Framework.
    /// Fica fora do domínio (Core) e implementa a porta IAutorRepository definida no domínio.
    /// </summary>
    public class AutorRepository : IAutorRepository
    {
        private readonly BibliotecaContext context;

        public AutorRepository(BibliotecaContext context)
        {
            this.context = context;
        }

        public uint Insert(Autor autor)
        {
            context.Add(autor);
            context.SaveChanges();
            return autor.Id;
        }

        public void Update(Autor autor)
        {
            context.Update(autor);
            context.SaveChanges();
        }

        public void Delete(uint id)
        {
            var autor = context.Autors.Find(id);
            if (autor != null)
            {
                context.Remove(autor);
                context.SaveChanges();
            }
        }

        public Autor? Get(uint id)
        {
            return context.Autors.Find(id);
        }

        public IEnumerable<Autor> GetAll()
        {
            return context.Autors.AsNoTracking();
        }

        public IEnumerable<Autor> GetAllOrderByNome()
        {
            var query = from Autor autor in context.Autors
                        orderby autor.Nome descending
                        select autor;
            return query.AsNoTracking();
        }

        public int GetCountAutores()
        {
            return context.Autors.Count();
        }

        public IEnumerable<Autor> GetByName(string nomeAutor)
        {
            var query = from autor in context.Autors
                        where autor.Nome.Contains(nomeAutor)
                        select autor;
            return query.AsNoTracking().ToList();
        }

        public IEnumerable<Autor> GetOrderByDescending()
        {
            var query = from autor in context.Autors
                        orderby autor.Nome descending
                        select autor;

            return context.Autors.
                OrderByDescending(autor => autor.Nome);
        }

        public IEnumerable<AutorDto> GetByNome(string nome)
        {
            var query = from autor in context.Autors
                        where autor.Nome.StartsWith(nome)
                        orderby autor.Nome
                        select new AutorDto
                        {
                            Id = autor.Id,
                            Nome = autor.Nome
                        };
            return query;
        }

        public DatatableResponse<Autor> GetDataPage(DatatableRequest request)
        {
            var autores = context.Autors.AsNoTracking();
            // total de registros na tabela
            var totalRecords = autores.Count();

            // filtra pelo campos de busca
            if (request.Search != null && request.Search.GetValueOrDefault("value") != null)
            {
                var searchValue = request.Search.GetValueOrDefault("value") ?? string.Empty;
                autores = autores.Where(autor => autor.Id.ToString().Contains(searchValue)
                                              || autor.Nome.ToLower().Contains(searchValue));
            }

            // ordenação pelas colunas permitidas
            if (request.Order != null && request.Order[0].GetValueOrDefault("column").Equals("0"))
            {
                if (request.Order[0].GetValueOrDefault("dir").Equals("asc"))
                    autores = autores.OrderBy(autor => autor.Id);
                else
                    autores = autores.OrderByDescending(autor => autor.Id);
            }
            else if (request.Order != null && request.Order[0].GetValueOrDefault("column").Equals("1"))
            {
                if (request.Order[0].GetValueOrDefault("dir").Equals("asc"))
                    autores = autores.OrderBy(autor => autor.Nome);
                else
                    autores = autores.OrderByDescending(autor => autor.Nome);
            }
            else if (request.Order != null && request.Order[0].GetValueOrDefault("column").Equals("2"))
            {
                if (request.Order[0].GetValueOrDefault("dir").Equals("asc"))
                    autores = autores.OrderBy(autor => autor.DataNascimento);
                else
                    autores = autores.OrderByDescending(autor => autor.DataNascimento);
            }

            // total de registros filtrados
            int countRecordsFiltered = autores.Count();
            // paginação que será exibida
            autores = autores.Skip(request.Start).Take(request.Length);
            return new DatatableResponse<Autor>()
            {
                Data = autores.ToList(),
                Draw = request.Draw,
                RecordsFiltered = countRecordsFiltered,
                RecordsTotal = totalRecords
            };
        }
    }
}
